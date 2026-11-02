"""Local branch-aware gates. Missing projects/tests/tools fail closed."""
import argparse
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ('python', 'javafx', 'android', 'unity')
UV = [shutil.which('uv')] if shutil.which('uv') else [sys.executable, '-m', 'uv']

def run(args, cwd=ROOT):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)

def branch_platform(branch):
    if branch in ('main', 'develop'):
        return 'python'
    suffix = branch.rsplit('/', 1)[-1]
    if '/' not in branch or suffix not in PLATFORMS:
        raise ValueError('Rama sin sufijo valido: usa tarea/python, tarea/javafx, tarea/android o tarea/unity')
    return suffix

def coverage(path):
    root = ET.parse(path).getroot()
    if root.tag == 'report':
        counter = next(c for c in root.findall('counter') if c.attrib['type'] == 'LINE')
        covered, missed = int(counter.attrib['covered']), int(counter.attrib['missed'])
        total = covered + missed
        rate = covered / total if total else 0
    else:
        total = int(root.attrib.get('lines-valid', '0'))
        rate = float(root.attrib.get('line-rate', '0')) if total else 0
    if rate < .8:
        raise ValueError(f'Cobertura {rate:.1%}; minimo 80%, sin promediar aplicaciones')
    print(f'Cobertura: {rate:.1%}')

def suite(platform, stage):
    project = ROOT / platform
    out = ROOT / '.artifacts' / platform
    out.mkdir(parents=True, exist_ok=True)
    if platform == 'python':
        run(UV + ['sync', '--locked', '--extra', 'dev', '--project', project])
        uv = UV + ['run', '--locked', '--extra', 'dev', '--project', project]
        run(uv + ['ruff', 'format', '--check', '.'], project)
        run(uv + ['ruff', 'check', '.'], project)
        run(uv + ['python', '-m', 'pytest', '--cov=src', '--cov-fail-under=80',
                  '--cov-report=term-missing', f'--cov-report=xml:{out / "coverage.xml"}',
                  f'--cov-report=html:{out / "html"}', f'--junitxml={out / "junit.xml"}'], project)
    elif platform in ('javafx', 'android'):
        wrapper = project / ('gradlew.bat' if os.name == 'nt' else 'gradlew')
        if not wrapper.is_file():
            raise ValueError(f'Falta {wrapper}; importa el proyecto real con Gradle Wrapper')
        tasks = ['test', 'jacocoTestReport'] if platform == 'javafx' else ['testDebugUnitTest', 'jacocoTestReport']
        report = project / ('build/reports/jacoco/test/jacocoTestReport.xml' if platform == 'javafx' else 'app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml')
        report.unlink(missing_ok=True)
        run([wrapper, '--no-daemon', '--rerun-tasks', *tasks], project)
        # A successful Gradle task with NO-SOURCE must not count as tests.
        results = list(project.glob('**/test-results/**/TEST-*.xml'))
        if not any(int(ET.parse(p).getroot().attrib.get('tests', '0')) > 0 for p in results):
            raise ValueError('No hay pruebas JUnit ejecutadas')
        coverage(report)
    else:
        editor = os.environ.get('UNITY_EDITOR')
        if not editor or not Path(editor).is_file():
            raise ValueError('Define UNITY_EDITOR con el Unity 6.3 real instalado')
        version = (project / 'ProjectSettings/ProjectVersion.txt').read_text()
        if '6000.3.' not in version:
            raise ValueError('El contrato requiere Unity 6.3 (6000.3.x)')
        assemblies = (project / 'coverage-assemblies.txt').read_text().splitlines()
        assemblies = [a.strip() for a in assemblies if a.strip() and not a.startswith('#')]
        if not assemblies or any('*' in a or 'Tests' in a for a in assemblies):
            raise ValueError('Declara assemblies propios exactos en unity/coverage-assemblies.txt')
        shutil.rmtree(out / 'coverage', ignore_errors=True)
        for mode in ('EditMode', 'PlayMode'):
            report = out / f'{mode}.xml'
            report.unlink(missing_ok=True)
            run([editor, '-batchmode', '-nographics', '-projectPath', project,
                 '-runTests', '-testPlatform', mode, '-testResults', report,
                 '-logFile', out / f'{mode}.log', '-enableCodeCoverage',
                 '-coverageResultsPath', out / 'coverage',
                 '-coverageOptions', 'generateAdditionalMetrics;generateHtmlReport;generateBadgeReport;assemblyFilters:' + ','.join('+' + a for a in assemblies)])
            result = ET.parse(report).getroot()
            if int(result.attrib.get('total', '0')) == 0 or result.attrib.get('result') != 'Passed':
                raise ValueError(f'{mode}: pruebas ausentes o fallidas')
        # Unity Code Coverage produces OpenCover. Measure only declared own assemblies.
        reports = list((out / 'coverage').glob('**/*opencov*.xml'))
        if not reports:
            raise ValueError('Falta informe OpenCover; instala Code Coverage y configura assemblyFilters propios')
        covered = total = 0
        for report in reports:
            for module in ET.parse(report).getroot().findall('.//Module'):
                if module.findtext('ModuleName', '') not in assemblies:
                    continue
                summary = module.find('Summary')
                if summary is not None:
                    covered += int(summary.attrib['visitedSequencePoints'])
                    total += int(summary.attrib['numSequencePoints'])
        if not total or covered / total < .8:
            raise ValueError('Unity: cobertura propia inferior al 80% o informe sin puntos medibles')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=('pre-commit', 'pre-push', 'ci', 'test'))
    p.add_argument('--branch')
    p.add_argument('--platform', choices=PLATFORMS)
    args, _ = p.parse_known_args()
    # CI has one contractual suite and must also work in source-only containers.
    if args.stage == 'ci':
        suite('python', args.stage)
        return
    if args.stage == 'test' and args.platform:
        suite(args.platform, args.stage)
        return
    branch = args.branch or subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if args.stage in ('pre-commit', 'pre-push') and branch in ('main', 'develop'):
        raise ValueError(f'Operacion bloqueada en {branch}; usa rama y Pull Request')
    if args.stage == 'pre-push':
        for line in sys.stdin:
            local_ref, local_sha, remote_ref, remote_sha = line.split()
            if remote_ref in ('refs/heads/main', 'refs/heads/develop'):
                raise ValueError(f'Push directo bloqueado a {remote_ref}')
            # Do not validate a different ref using tests from the current checkout.
            if local_ref != 'refs/heads/' + branch:
                raise ValueError('Push solo de la rama actual; no tags, borrados ni multiples ramas')
    platform = args.platform or branch_platform(branch)
    if args.stage == 'ci':
        platform = 'python'  # Contract 3.5, 6.3: CI tests Python exclusively.
    suite(platform, args.stage)

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, ET.ParseError, StopIteration) as exc:
        print(f'BLOQUEADO: {exc}', file=sys.stderr)
        sys.exit(1)
