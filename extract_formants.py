import timeside
from timeside.core import get_processor
import sys
from numpy import mean, std

def analyze_speech(nbuffs=1000, use_vad=False):
    decoder = get_processor('live_decoder')(num_buffers=nbuffs, vad=use_vad)
    decoder.output_blocksize = 4096
    decoder.output_samplerate = 8000
    decoder.output_channels = 1

     # apply Hamming with numpy before processing
    featplan = ['lpc: LPC LPCNbCoeffs=12 blockSize=256 stepSize=64',
                'loud: Loudness FFTWindow=Hamming LMode=Total blockSize=256 stepSize=128',
                'autopeaks: Energy blockSize=256 stepSize=128 > AutoCorrelationPeaksIntegrator ACPNbPeaks=3 ACPInterPeakMinDist=3 NbFrames=32 StepNbFrames=8']
#                'magspec: MagnitudeSpectrum blockSize=512 stepSize=128 '
                

    level = get_processor('level')()
    aubio = get_processor('aubio_pitch')(blocksize_s=256, stepsize_s=64)
    yaaf = get_processor('yaafe')(featplan, 8000)
    # irit = get_processor('irit_speech_4hz')()
    # iritgraph = get_processor('grapher_irit_speech_4hz_segments')
    # odf = get_processor('onset_detection_function')()
    # odfgraph = get_processor('grapher_onset_detection_function')()

    pipe = (decoder | aubio | yaaf | level) # | odf | irit)
    pipe.run()
#    print 'Pauses: %s' % str(decoder.pauses)
    print
    loud_mean, loud_std = yaaf.loud_mean(), yaaf.loud_std()
    level_rms, level_max = level.results['level.rms'].data[0], level.results['level.max'].data[0]
    pitch_mean, pitch_std = mean(aubio.results['aubio_pitch.pitch'].data), std(aubio.results['aubio_pitch.pitch'].data)
    syllrate_mean, syllrate_std = yaaf.syll_rate_mean(), yaaf.syll_rate_std()
    fps = yaaf.fp_count

    
    
    print 'Average Loudness = %.1f sons\t(level = %.1f dBFS)' % (yaaf.loud_mean(),
                                                                 level.results['level.rms'].data[0])
    print 'Average articulation rate = %.2f syllables/sec' % (yaaf.syll_rate_mean())
    print 'Total filled pauses: %d' % fps
    return pipe


if __name__ == '__main__':
    #    fname = sys.argv[1]
    if len(sys.argv) > 1:
        nbuffs = int(sys.argv[1])
    else:
        nbuffs = 1000
    use_vad = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'
    analyze_speech(nbuffs, use_vad)

