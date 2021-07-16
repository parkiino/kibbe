from click.testing import CliRunner
from es import es
import subprocess

def test_es(mocker):
    runner = CliRunner()
    mocker.patch('subprocess.run')
    result = runner.invoke(es, ['--data-dir', '/tmp/es-data'])
    assert 'path.data=/tmp/es-data'in result.output
    # assert not result.exception
    assert subprocess.run.call_count == 1
