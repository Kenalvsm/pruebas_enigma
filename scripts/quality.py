"""Gates de calidad exclusivos de Python; el resto de ramas se ignora."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ('python',)
BRANCH_WORD = 'python'
PROTECTED = ('main', 'develop')
UV = [shutil.which('uv')] if shutil.which('uv') else [sys.executable, '-m', 'uv']


def run(args, cwd=ROOT):
    print('+', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def is_python_branch(branch):
    """Solo cuentan las ramas cuyo ultimo segmento es exactamente python."""
    return branch.rsplit('/', 1)[-1] == BRANCH_WORD


def current_branch():
    return subprocess.check_output(
        ['git', 'branch', '--show-current'], cwd=ROOT, text=True
    ).strip()


def suite(stage):
    project = ROOT / 'python'
    out = ROOT / '.artifacts' / 'python'
    out.mkdir(parents=True, exist_ok=True)
    run(UV + ['sync', '--locked', '--project', project])
    uv = UV + ['run', '--locked', '--project', project]
    run(uv + ['ruff', 'format', '--check', '.'], project)
    run(uv + ['ruff', 'check', '.'], project)
    run(
        uv
        + [
            'pytest',
            '--cov=src',
            '--cov-fail-under=80',
            '--cov-report=term-missing',
            f'--cov-report=xml:{out / "coverage.xml"}',
            f'--cov-report=html:{out / "html"}',
            f'--junitxml={out / "junit.xml"}',
        ],
        project,
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=('pre-commit', 'pre-push', 'ci', 'test'))
    p.add_argument('--branch')
    p.add_argument('--platform', choices=PLATFORMS)
    args, _ = p.parse_known_args()
    # CI (contrato 3.5 y 6.3) y las ejecuciones manuales son solo Python y
    # deben funcionar en contenedores sin Git ni rama disponible.
    if args.stage in ('ci', 'test'):
        suite(args.stage)
        return
    branch = args.branch or current_branch()
    if branch in PROTECTED:
        raise ValueError(f'Operacion bloqueada en {branch}; usa rama y Pull Request')
    if args.stage == 'pre-push':
        for line in sys.stdin:
            local_ref, _, remote_ref, _ = line.split()
            if remote_ref in ('refs/heads/main', 'refs/heads/develop'):
                raise ValueError(f'Push directo bloqueado a {remote_ref}')
            if local_ref != 'refs/heads/' + branch:
                raise ValueError(
                    'Push solo de la rama actual; no tags, borrados ni multiples ramas'
                )
    if not is_python_branch(branch):
        print(
            f'Rama {branch} ignorada: los gates solo validan ramas que acaban en '
            f'{BRANCH_WORD}',
            flush=True,
        )
        return
    suite(args.stage)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'BLOQUEADO: {exc}', file=sys.stderr)
        sys.exit(1)
