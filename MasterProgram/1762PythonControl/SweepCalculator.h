//Header file
//Functions needed to calculate things for frequency sweep program.


#pragma once
#include <SPI.h>
#include <stdint.h>

struct stepFlag 
{
	double step;
	bool flag;
};

struct start_stop
{
	double start;
	double stop;
};


stepFlag calcStepTime(double stepSize, double stepRate, double maxStepTime = 0.000524288);

stepFlag calcStepSize(double stepTime, double stepRate, double maxStepSize = 100000);

start_stop calcStartStop(double centerFreq, double span, double maxFreq, double minFreq);
//maxFreq and minFreq will typically be limits such as the frequencies where the nearest motional sidebands are
//span is how far you want the sweep to go
//if span takes you outside of the max or min, the used start and stop frequencies will be set to max or min respectively.