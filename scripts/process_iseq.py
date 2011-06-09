#!/usr/bin/env python
# File created on 30 Mar 2011
from __future__ import division

__author__ = "Greg Caporaso"
__copyright__ = "Copyright 2011, The QIIME project"
__credits__ = ["Greg Caporaso"]
__license__ = "GPL"
__version__ = "1.2.1-dev"
__maintainer__ = "Greg Caporaso"
__email__ = "gregcaporaso@gmail.com"
__status__ = "Development"

from glob import glob
from os.path import split, splitext
from cogent.util.misc import create_dir
from qiime.util import (parse_command_line_parameters, make_option,
                        iseq_to_qseq_fields, gzip_open)
from qiime.format import illumina_data_to_fastq
from qiime.split_libraries_illumina import get_illumina_qual_chars

script_info = {}
script_info['brief_description'] = "Given a directory of per-swath qseq files, this script generates a single fastq per lane."
script_info['script_description'] = ""
script_info['script_usage'] = [("","Generate fastq files from all lanes of read 1 data in the current directory.","process_qseq.py -i ./ -o ./fastq/ -r 1"),
                               ("","Generate fastq files from all lanes of read 2 data in the current directory, truncating the sequences after the first 12 bases.","process_qseq.py -i ./ -o ./fastq/ -r 2 -b 12")]
script_info['output_description']= ""
script_info['required_options'] = [
 make_option('-i','--input_fps',type='existing_filepaths',
  help='the input filepaths (comma-separated if more than one)'),
 make_option('-o','--output_dir',help='the output directory'),
 make_option('-b','--barcode_length',type='int',
  help='length of the barcode'),
]
script_info['optional_options'] = [
 make_option('--barcode_in_header',action='store_true',
  help='pass if barcode is in the header index'+\
  ' field (rather than at the beginning of the sequence)',default=False),
 make_option('--barcode_qual_c',type='choice',
  choices=list(get_illumina_qual_chars()),
  help='if no barcode quality string is available, score each base with'+\
  ' this quality [default: %default]',default='b')
]
script_info['version'] = __version__

def main():
    option_parser, opts, args =\
       parse_command_line_parameters(**script_info)
    
    input_fps = opts.input_fps
    output_dir = opts.output_dir
    create_dir(output_dir)
    barcode_length = opts.barcode_length
    barcode_in_header = opts.barcode_in_header
    barcode_qual_c = opts.barcode_qual_c
    
    for input_fp in input_fps:
        if input_fp.endswith('.gz'):
            open_f = gzip_open
            input_basename = split(splitext(splitext(input_fp)[0])[0])[1]
        else:              
            input_basename = split(splitext(input_fp)[0])[1]
            open_f = open
        sequence_output_fp =  '%s/%s.fastq' % (output_dir,input_basename)
        sequence_output_f = open(sequence_output_fp,'w')              
        barcode_output_fp =  '%s/%s_barcodes.fastq' % (output_dir,input_basename)
        barcode_output_f = open(barcode_output_fp,'w')
        for line in open_f(input_fp):
            common_fields, sequence, sequence_qual, barcode, barcode_qual =\
             iseq_to_qseq_fields(line, barcode_in_header, barcode_length, barcode_qual_c)
            
            sequence_s = illumina_data_to_fastq((common_fields[0],
                                                 common_fields[1],
                                                 common_fields[2],
                                                 common_fields[3],
                                                 common_fields[4],
                                                 common_fields[5],
                                                 common_fields[6],
                                                 common_fields[7],
                                                 sequence,
                                                 sequence_qual))
            sequence_output_f.write('%s\n' % sequence_s)
            
            barcode_s = illumina_data_to_fastq((common_fields[0],
                                                common_fields[1],
                                                common_fields[2],
                                                common_fields[3],
                                                common_fields[4],
                                                common_fields[5],
                                                common_fields[6],
                                                common_fields[7],
                                                barcode,
                                                barcode_qual),barcode_length)
            barcode_output_f.write('%s\n' % barcode_s)
        sequence_output_f.close()
        barcode_output_f.close()
        
if __name__ == "__main__":
    main()