#!/usr/bin/python
import sys
import os
import inspect
import subprocess as sub
import shlex

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import common
import config as cfg
	
	
	
	
	
	
	
	
	
	
def runCommand(cmd, outfile=False, overwrite=False):
	cmd = shlex.split(cmd)
	
	if outfile:
		if os.path.exists(outfile) and not overwrite:
			stdout = open(outfile, 'a')
			stdout.flush()
		else:
			stdout = open(outfile, 'w')
		p = sub.Popen(cmd, stdout=stdout, stderr=sub.STDOUT)
		
	else:
		p = sub.Popen(cmd)
		
	p.wait()
	










def runOne(fastqFile, mapIdx, trim, statsDir, tempDir, samDir, bowtie, samtools):
  
	#get environment prepared#
	mapVars = cfg.Map()

 	fastqFile = common.zipping(fastqFile)
	
	sampleName = os.path.basename(fastqFile)[:-6]
  
	statFile = statsDir + sampleName + '.map.stats.txt'

  
  
	#run bowtie#
	cmd =	[bowtie] + \
			mapVars.bowtieOptions +	\
			[
			'-5', str(trim[0]), 
			'-3', str(trim[1]), 
			mapIdx, 
			fastqFile, 
			tempDir + sampleName + '.sam'
			]
	cmd = ' '.join(cmd)	
	runCommand(cmd, outfile=statFile, overwrite=True)
#	print 'mapping done\n'
	
	
	
	#sam to bam#
	cmd =	[
			samtools, 'view', '-bS', 
		  	'-o', tempDir + sampleName + '.bam',
		 	tempDir + sampleName + '.sam'
			]
	cmd = ' '.join(cmd)
	runCommand(cmd)
#	print 'sam converted to bam\n'
	

	
	#sort bam#
	cmd =	[
			samtools, 'sort', 
		 	tempDir + sampleName + '.bam', 
			tempDir + sampleName + '.sorted'
			]
	
	cmd = ' '.join(cmd)
	runCommand(cmd)
#	print 'bam sorted\n'
	
	
	
	#remove duplicates#
	cmd =	[
			samtools, 'rmdup', '-s', 
			tempDir + sampleName + '.sorted.bam',
			tempDir + sampleName + '.unique.bam'
			]
	cmd = ' '.join(cmd)
	runCommand(cmd, outfile=statFile)
#	print 'duplicates removed\n'
	
	
	#bam to sam#
	cmd =	[
			samtools, 'view', '-h', 
		  	'-o', samDir + sampleName + '.unique.sam',
		 	tempDir + sampleName + '.unique.bam'
			]
	cmd = ' '.join(cmd)
	runCommand(cmd)
#	print 'bam converted to sam\n'


	
	printText = '\t\tFinished mapping and removing PCR duplicates for ' + os.path.basename(fastqFile)
	print(printText)




	
