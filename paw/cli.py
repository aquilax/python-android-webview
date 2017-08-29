import os
import click
import configparser
from shutil import copytree, rmtree
from string import Template

BUILD_SCRIPT_NAME = 'build.gradle'
MANIFEST_NAME = 'AndroidManifest.xml'
ACTIVITY_NAME = 'MainActivity.java'
LAUNCHER_ICON_NAME = 'ic_launcher.png'


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))


@cli.command()
@click.argument('config')
@click.argument('output', type=click.Path(exists=False))
def generate(config: str, output: str):
    config = _load_config(config)
    """Generates new template"""
    click.echo(click.format_filename(output))
    if not os.path.exists(output):
        os.makedirs(output)
    basePath = os.path.dirname(os.path.realpath(__file__))
    templatesPath = os.path.join(basePath, 'templates')
    copyTemplates(templatesPath, output, config)
    if config['copy_from']:
        _copy_project(config['copy_from'], output + '/')
    copy_icons(output, config)


@cli.command()
def build():
    """Builds the android application"""


def _load_config(config_file: str):
    base = os.path.dirname(config_file)
    config = configparser.ConfigParser()
    config.read(config_file)
    app = config['App']
    return {
        'package_name': app['package_name'],
        'application_name': app['application_name'],
        'copy_from': os.path.join(base, app['copy_from']),
        'svg_icon': os.path.join(base, app['svg_icon']),
        'version_code': app['version_code'],
        'version_name': app['version_name'],
    }


def create_icon(path, svg_icon, size):
    cmd = 'inkscape {svg_icon} -w {width} -h {height} --export-png={icon}'.format(
        svg_icon=svg_icon, width=size, height=size, icon=os.path.join(path, LAUNCHER_ICON_NAME))
    os.system(cmd)


def copy_icons(output: str, config: dict):
    sizes = [{
        'name': 'mipmap-mdpi',
        'd': 48,
    }, {
        'name': 'mipmap-hdpi',
        'd': 72,
    }, {
        'name': 'mipmap-xhdpi',
        'd': 96,
    }, {
        'name': 'mipmap-xxhdpi',
        'd': 144,
    }, {
        'name': 'mipmap-xxxhdpi',
        'd': 192,
    }]
    for size in sizes:
        path = os.path.join(output, 'src', 'main', 'res', size['name'])
        _create_path(path)
        if config['svg_icon']:
            create_icon(path, config['svg_icon'], size['d'])


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


def copyTemplates(templates: str, output: str, config):
    _copyBuildScript(templates, output, config)
    _copyManifest(templates, output, config)
    _copyActivity(templates, _get_activity_path(output, config['package_name']), config)


if __name__ == '__main__':
    cli()
