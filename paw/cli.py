import os
import click
from shutil import copytree, rmtree
from string import Template

BUILD_SCRIPT_NAME = 'build.gradle'
MANIFEST_NAME = 'AndroidManifest.xml'
ACTIVITY_NAME = 'MainActivity.java'


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
@click.argument('output', type=click.Path(exists=False))
@click.argument('package')
@click.option('--copy-from')
def generate(output: str, package: str, copy_from: str=''):
    """Generates new template"""
    click.echo(click.format_filename(output))
    if not os.path.exists(output):
        os.makedirs(output)
    basePath = os.path.dirname(os.path.realpath(__file__))
    templatesPath = os.path.join(basePath, 'templates')
    copyTemplates(templatesPath, output, package)
    if copy_from:
        _copy_project(copy_from, output + '/')
    copy_icons(output)


def copy_icons(output):
    sizes = ['mipmap-hdpi', 'mipmap-mdpi', 'mipmap-xhdpi', 'mipmap-xxhdpi', 'mipmap-xxxhdpi']
    for size in sizes:
        _create_path(os.path.join(output, 'src', 'main', 'res', size))


@cli.command()
def build():
    """Builds the android application"""


def _create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def _render(source, destination, data):
    file_name = os.path.basename(source)
    with open(source, 'r') as template_file:
        t = Template(template_file.read()).substitute(data)
    with open(os.path.join(destination, file_name), 'w') as destination_file:
        destination_file.write(t)
    return True


def _copy_project(source, output):
    destination = os.path.join(output, 'src', 'main', 'assets', 'www')
    _create_path(destination)
    rmtree(destination)
    copytree(source, destination)


def _get_activity_path(output: str, package: str):
    dirs = package.split('.')
    targetPath = os.path.join(output, 'src', 'main', 'java', *dirs)
    _create_path(targetPath)
    return targetPath


def _copyBuildScript(templates, output, data):
    return _render(os.path.join(templates, BUILD_SCRIPT_NAME), output, data)


def _copyManifest(templates, output, data):
    targetPath = os.path.join(output, 'src', 'main')
    click.echo(click.format_filename(targetPath))
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    return _render(os.path.join(templates, MANIFEST_NAME), targetPath, data)


def _copyActivity(templates, output, data):
    return _render(os.path.join(templates, ACTIVITY_NAME), output, data)


def copyTemplates(templates: str, output: str, package: str):
    data = {
        'application_name': 'Test application',
        'package_name': package
    }
    _copyBuildScript(templates, output, data)
    _copyManifest(templates, output, data)
    _copyActivity(templates, _get_activity_path(output, package), data)


if __name__ == '__main__':
    cli()
