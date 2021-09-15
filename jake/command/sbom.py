import argparse

from cyclonedx.model.bom import Bom
from cyclonedx.output import BaseOutput, get_instance, OutputFormat, SchemaVersion, DEFAULT_SCHEMA_VERSION
from cyclonedx.parser import BaseParser
from cyclonedx.parser.environment import EnvironmentParser
from cyclonedx.parser.requirements import RequirementsFileParser
from . import BaseCommand


class SbomCommand(BaseCommand):

    def handle_args(self):
        self._arguments.sbom_input_type
        bom = Bom.from_parser(self._get_parser())

        output_format = OutputFormat.XML
        if self._arguments.sbom_output_format == 'json':
            output_format = OutputFormat.JSON

        schema_version = DEFAULT_SCHEMA_VERSION
        if self._arguments.sbom_schema_version:
            schema_version = SchemaVersion['V{}'.format(str(self._arguments.sbom_schema_version).replace('.', '_'))]

        output: BaseOutput = get_instance(bom=bom, output_format=output_format, schema_version=schema_version)

        if self._arguments.sbom_output_file:
            # Output to a file
            output.output_to_file(filename=self._arguments.sbom_output_file, allow_overwrite=True)
        else:
            # Output to STDOUT
            print(output.output_as_string())

    def setup_argument_parser(self, subparsers: argparse._SubParsersAction):
        parser: argparse.ArgumentParser = subparsers.add_parser(
            'sbom',
            help='generate a CycloneDX software-bill-of-materials (no vulnerabilities)',
        )

        parser.add_argument('-it', '--input-type',
                            help='how jake should find the packages from which to generate your SBOM.'
                                 'ENV = Read from the current Python Environment; PIP = read from a requirements.txt; '
                                 'POETRY = read from a poetry.lock. '
                                 '(Default = ENV)',
                            metavar='TYPE', choices={'ENV', 'PIP', 'POETRY'}, default='ENV', dest='sbom_input_type')
        parser.add_argument('-o', '--output-file', help='Specify a file to output the SBOM to', metavar='PATH/TO/FILE',
                            dest='sbom_output_file')
        parser.add_argument('--output-format', help='SBOM output format (default = xml)', choices={'json', 'xml'},
                            default='xml', dest='sbom_output_format')
        parser.add_argument('--schema-version', help='CycloneDX schema version to use (default = 1.3)',
                            choices={'1.3', '1.2', '1.1', '1.0'}, default='1.3',
                            dest='sbom_schema_version')

    def _get_parser(self) -> BaseParser:
        if self._arguments.sbom_input_type == 'ENV':
            return EnvironmentParser()

        if self._arguments.sbom_input_type == 'PIP':
            return RequirementsFileParser(requirements_file='requirements.txt')

        raise NotImplementedError
