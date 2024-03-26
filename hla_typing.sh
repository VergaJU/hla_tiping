#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Run HLA typining with arcasHLA, OptiTyie and T1K."
   echo
   echo "Syntax: scriptTemplate [-i|t|h|]"
   echo "options:"
   echo "t     number of threads. Default: 8"
   echo "o     output directory. Default: hla_typing_out"
   echo "s     single or paired end. Default: single"
   echo "h     Print this Help."
   echo
}

############################################################
############################################################

output_dir="hla_typing_out"
threads=8

# Get the options
while getopts ":hf:i:t:o:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      t) # Threads
         threads=$OPTARG;;
      o) # Output
         output_dir=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option."
         echo "run the script with -h to see usage."
         exit;;
   esac
done




EXTRACT (){
    bampath=$1
    output=$2
    threads=$3
    sudo docker compose --profile arcas run	--rm arcas_hla arcasHLA extract --single -o /home/$output /home/$bampath -t $threads
}


ARCAS (){
    fastq=$1
    output=$2/arcasHLA/
    threads=$3
    sudo docker compose --profile arcas run	--rm arcas_hla arcasHLA genotype /home/$fastq -o /home/$output -t $threads --single
}


OPTITYPE(){
    fastq=$1
    output=$2/optitype/
    bamfile=$3
    sudo docker compose --profile optitype run --rm optitype OptiTypePipeline.py -i /home/$fastq --rna -o /home/$output --prefix $bamfile
}

T1K(){
    fastq=$1
    output=$2/t1k/
    threads=$3
    sudo docker compose --profile t1k run --rm t1k run-t1k -u /home/$fastq --preset hla -f /app/T1K/hlaidx/hlaidx_rna_seq.fa --od /home/$output -t $threads
}

AGGREGATE(){
    sample_out=$1
    bamfile=$2
    sudo docker compose --profile aggregate run --rm aggregate aggregate.py /home/$sample_out $bamfile
}

# create output directory
mkdir $output_dir


for bampath in $(find data/ -type f -not -name "*.bai"); do
    bamfile=$(basename ${bampath%.*})
    bamdir=$(basename $(dirname $bampath))
    sample_out=${output_dir}"/"${bamdir}
    # create repo for file:
    echo "Processing file $bamfile..."
    echo "Extracting reads for Chr6"
    EXTRACT $bampath $sample_out $threads
    # get fastq location
    fastq=$(find $sample_out -name "*.fq*")
    # arcasHLA
    echo "running arcasHLA..."
    ARCAS $fastq $sample_out $threads
    echo "running optitype..."
    OPTITYPE $fastq $sample_out $bamfile
    echo "running T1K..."
    T1K $fastq $sample_out $threads
    echo "aggregate results..."
    AGGREGATE $sample_out $bamfile
done
