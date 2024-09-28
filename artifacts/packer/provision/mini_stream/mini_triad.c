#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef USEM5OPS
#include <gem5/m5ops.h>
#endif

#ifdef LIKWID_PERFMON
#include <likwid-marker.h>
#endif

#ifndef STREAM_TYPE
#define STREAM_TYPE double
#endif

#ifndef MEM_ALIGN
#define MEM_ALIGN 4096
#endif

typedef __attribute__(( aligned(MEM_ALIGN))) STREAM_TYPE FLOAT_T;
typedef uint64_t TIME_T;
typedef uint64_t PERF_T;

void print_performance( const char *name, const char *unit, PERF_T work, TIME_T *t, int reps) {
	TIME_T min = t[0];
	TIME_T max = t[0];
	TIME_T sum = t[0];
	double mean = 0.0;
	double sdev = 0.0;
	for (int k = 1; k < reps; k++) {
		sum += t[k];
		min = t[k] < min ? t[k] : min;
		max = t[k] > max ? t[k] : max;
	}
	mean = (double) sum / reps;
	for (int k = 0; k < reps; k++) {
		sdev += (t[k]-mean)*(t[k]-mean);
	}
	if (reps>1)
		sdev = sqrt(sdev/(reps-1));

	printf("%s Performance [G%s/s]: max:%11.6f min:%11.6f mean:%11.6f | max:%11.6E min:%11.6E mean:%11.6E std:%11.6E\n",
			name, unit, (double) work / min, (double) work / max, (double) work / mean, 
			            max*1.0E-09, min*1.0E-09, mean*1.0E-09, sdev*1.0E-09);
}

int main(int argc, char *argv[]) {
#ifdef __COMPILE_COMMAND__
	printf("BENCHMARK: %s \tCFLAGS: %s\n", __FILE__, __COMPILE_COMMAND__);
#endif
#ifdef LIKWID_PERFMON
    LIKWID_MARKER_INIT;
    #pragma omp parallel
    {
        LIKWID_MARKER_REGISTER("Compute");
    }
#endif
    FLOAT_T *a;
    FLOAT_T *b;
    FLOAT_T *c;
    
    TIME_T *t;
    
    struct timespec t0, t1;
	
    int nthr = 1;
    int size = (int)strtol(argv[1], NULL, 10);
    int reps = (int)strtol(argv[2], NULL, 10);
    FLOAT_T s = 3.0;

#ifdef _OPENMP
    nthr = omp_get_max_threads();
#endif
    printf("nthr=%i size=%i sizeMB=%i, reps=%i\n", nthr, size, size*sizeof(FLOAT_T) / (1024*1024),reps);

    posix_memalign((void **) &a, MEM_ALIGN, (size * sizeof(FLOAT_T)));
    posix_memalign((void **) &b, MEM_ALIGN, (size * sizeof(FLOAT_T)));
    posix_memalign((void **) &c, MEM_ALIGN, (size * sizeof(FLOAT_T)));
    posix_memalign((void **) &t, MEM_ALIGN, (reps * sizeof(TIME_T)));

    // Initialize arrays
#pragma omp parallel for
	for (int i=0; i<size; i++) {
        a[i] = 1.0;
        b[i] = 2.0;
        c[i] = 0.0;
    }

	for(int k = 0; k < reps; k++) {
		clock_gettime(CLOCK_MONOTONIC, &t0);
#ifdef USEM5OPS
		m5_reset_stats(0,0);
#endif
#pragma omp parallel
{
#ifdef LIKWID_PERFMON
	LIKWID_MARKER_START("Compute");
#endif
#pragma omp for
	    for (int i=0; i<size; i++) {
            c[i] = a[i]+s*b[i];
        }
#ifdef LIKWID_PERFMON
	LIKWID_MARKER_STOP("Compute");
#endif
}
#ifdef USEM5OPS
		m5_dump_stats(0,0);
#endif
		clock_gettime(CLOCK_MONOTONIC, &t1);
		t[k] = (TIME_T) ((t1.tv_sec - t0.tv_sec) * 1e9 + (t1.tv_nsec - t0.tv_nsec));
	}

    print_performance("mini_triad", "B", 3 * sizeof(FLOAT_T) * size, t, reps);
	
    free(a);
    free(b);
    free(c);
    free(t);

#ifdef LIKWID_PERFMON
    LIKWID_MARKER_CLOSE;
#endif
}
