#!/usr/bin/env python

import sys
import os
import re
import json
import argparse
import logging as log

from datetime import date
from os.path import isfile
from argparse import RawTextHelpFormatter


import uuid
from subprocess import PIPE, STDOUT, run

def run_command(command, message = ''):
    '''Outputs message and command to log, runs command and returns output.'''
    if type(command) == list:
        command = ' '.join(command)

    if message: 
        log.info(''.join([message,'\n\n\t', command,'\n']))
    
    output = run(command, shell=True, stdout=PIPE, stderr=PIPE)
    
    if message:
        stderr = '\t' + output.stderr.decode('utf-8')
        stderr = re.sub('\n','\n\t',stderr)
        if len(stderr) > 1:
            log.info(stderr)
        
    return output

def check_path(path):
    '''Check if path exists and if it is terminated by "/".'''
    if not os.path.isdir(path):
        run_command(['mkdir',path])
        
    if path[-1] != '/': path += '/'
        
    return path

def remove_files(files, keep_files):
    '''Removes intermediate files.'''
    if keep_files:
        return

    if type(files) == list:
        for file in files:
            run_command(['rm -rf',file])
    else:
        run_command(['rm -rf',files])
        

def create_temp(temp):
    '''Generates name for temporary folder.'''
    temp = check_path(temp)
    temp_folder = ''.join([temp,'arcas_' + str(uuid.uuid4())])
    return check_path(temp_folder)

def hline():
    log.info('-'*80)

def index_bam(bam):
    '''Attempts to index BAM if .bai file is not found.'''
    if not isfile(''.join([bam, '.bai'])):
        run_command(['samtools', 'index', bam], 
                    '[extract] indexing bam: ')
                    
    if not isfile(''.join([bam, '.bai'])):
        sys.exit('[extract] Error: unable to index bam file.')

def extract_reads(bam, outdir, paired, unmapped, alts, temp, threads):
    '''Extracts reads from chromosome 6 and alts/decoys if applicable.'''
    
    log.info(f'[extract] Extracting reads from {bam}')
    
    file_list = []
    sample = os.path.splitext(os.path.basename(bam))[0]
    
    # Index bam
    index_bam(bam)
    
    hla_filtered = ''.join([temp, sample, '.hla.sam'])
    file_list.append(hla_filtered)
        
    # Get bam header to check for chromosome nomenclature
    output = run_command(['samtools', 'view', '-@'+threads, '-H', bam])
    header = output.stdout.decode('utf-8')
    
    if 'SN:chr' in header: 
        chrom = 'chr6'
    else: 
        chrom = '6'

    # Extract BAM header
    message = '[extract] Extracting chromosome 6: '
    command = ['samtools', 'view', '-H', '-@'+threads]
    command.extend([bam, '-o', hla_filtered])
    run_command(command, message)
    
    # Extracted reads mapped to chromosome 6
    message = '[extract] Extracting chromosome 6: '
    command = ['samtools', 'view', '-@'+threads]
    if paired: command.append('-f 2')
    else: command.append('-F 4')
    command.extend([bam, chrom, '>>', hla_filtered])
    run_command(command, message)
    
    # Extract unmapped reads
    if unmapped:
        message = '[extract] Extracting unmapped reads: '
        command = ['samtools', 'view', '-@'+threads]
        
        if paired: command.append('-f 12')
        else: command.append('-f 4')
        
        command.extend([bam, '>>', hla_filtered])
        run_command(command, message)
    
    # Check for alts in header and extract reads if present
    for alt in alts:
        if alt in header:
            command = ['samtools', 'view', '-@'+threads]
            
            if paired: command.append('-f 2')
            else: command.append('-F 4')
            
            command.extend([bam, alt+':', '>>', hla_filtered])
            run_command(command)

    # Sort and convert to BAM
    hla_sorted = ''.join([temp, sample, '.hla.sorted.bam'])
    file_list.append(hla_sorted)
    file_list.append(hla_sorted + '.bai')
    message = '[extract] Sorting bam: '
    command = ['samtools', 'sort', '-n', '-@'+threads, 
                hla_filtered, '-o', hla_sorted]
    run_command(command, message)

    # Convert BAM to FASTQ and compress
    message = '[extract] Converting bam to fastq: '
    command = ['bedtools', 'bamtofastq', '-i', hla_sorted]
    if paired:
        fq1 = ''.join([outdir, sample, '.extracted.1.fq'])
        fq2 = ''.join([outdir, sample, '.extracted.2.fq'])
        command.extend(['-fq', fq1, '-fq2', fq2])
        run_command(command, message)
        
        run_command(['pigz', '-f', '-p', threads, '-S', '.gz', fq1])
        run_command(['pigz', '-f', '-p', threads, '-S', '.gz', fq2])
        
    else:
        fq = ''.join([outdir, sample, '.extracted.fq'])
        command.extend(['-fq', fq])
        run_command(command, message)
        run_command(['pigz', '-f', '-p', threads, '-S', '.gz', fq])



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog='extract',
                                     usage='%(prog)s [options] BAM file',
                                     add_help=False,
                                     formatter_class=RawTextHelpFormatter)
    
    
    parser.add_argument('bam', 
                        type=str, 
                        help='/path/to/sample.bam')
    
    parser.add_argument('-h',
                        '--help', 
                        action = 'help',
                        help='show this help message and exit\n\n',
                        default=argparse.SUPPRESS)
                        
    parser.add_argument('--log', 
                    type=str,
                    help='log file for run summary\n  '+
                         'default: sample.extract.log\n\n',
                    default=None, 
                    metavar='')
                        
    parser.add_argument('--single', 
                        action = 'count',
                        help='single-end reads\n  default: False\n\n',
                        default=True)    
    
    parser.add_argument('--unmapped', 
                        action = 'count',
                        help='include unmapped reads\n  default: False\n\n',
                        default=False)
                        
    parser.add_argument('-o', '--outdir', 
                        type=str,
                        help='out directory\n\n',
                        default='./', metavar='')
                        
    parser.add_argument('--temp', 
                        type=str,
                        help='temp directory\n\n',
                        default='/tmp/', metavar='')
                        
    
    parser.add_argument('-t',
                        '--threads', 
                        type = str,
                        default='1')
    
    parser.add_argument('-v',
                        '--verbose', 
                        action = 'count',
                        default=False)

    args = parser.parse_args()

    outdir = check_path(args.outdir)
    temp = create_temp(args.temp)
    
    sample = os.path.basename(args.bam).split('.')[0]
    
    datDir = os.path.dirname(os.path.realpath(__file__)) + '/../dat/'
    
    # Set up log file
    if args.log:
        log_file = args.log
    else:
        log_file = ''.join([outdir,sample,'.extract.log'])
    with open(log_file, 'w'):
        pass
    if args.verbose:
        handlers = [log.FileHandler(log_file), log.StreamHandler()]
        
        log.basicConfig(level=log.DEBUG, 
                        format='%(message)s', 
                        handlers=handlers)
    else:
        handlers = [log.FileHandler(log_file)]
            
        log.basicConfig(level=log.DEBUG, 
                        format='%(message)s', 
                        handlers=handlers)
        
    log.info('')
    hline()
    log.info(f'[log] Date: %s', str(date.today()))
    log.info(f'[log] Sample: %s', sample)
    log.info(f'[log] Input file: %s', args.bam)
    log.info('[log] Read type: {}-end'
             .format( 'paired' if not args.single else 'single'))
    hline()
    
    # Load names of regions outside chr6 with HLA loci
    #with open(datDir + '/info/decoys_alts.p', 'rb') as file:
    #    alts = pickle.load(file)
    with open(datDir + 'info/decoys_alts.json', 'r') as file:
        alts = json.load(file)


    extract_reads(args.bam,
                    outdir,
                    not args.single,
                    args.unmapped,
                    alts,
                    temp,
                    args.threads)

    remove_files(temp, True)
    
    hline()
    log.info('')
