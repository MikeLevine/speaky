import timeside
from timeside.core import get_processor
import sys

def analyze_speech(nbuffs=1000, use_vad=False):
    decoder = get_processor('live_decoder')(num_buffers=nbuffs, vad=use_vad)
    decoder.output_blocksize = 4096
    decoder.output_samplerate = 8000
    decoder.output_channels = 1

     # apply Hamming with numpy before processing
    featplan = ['lpc: LPC LPCNbCoeffs=12 blockSize=256 stepSize=64',
                'loud: Loudness FFTWindow=Hamming LMode=Total blockSize=256 stepSize=128',
                'energy: Energy blockSize=256 stepSize=128 > AutoCorrelationPeaksIntegrator ACPNbPeaks=5 ACPInterPeakMinDist=5 NbFrames=32 StepNbFrames=16']
#                'magspec: MagnitudeSpectrum blockSize=512 stepSize=128 '
                

    level = get_processor('level')()
    aubio = get_processor('aubio_pitch')(blocksize_s=256, stepsize_s=64)
    yaaf = get_processor('yaafe')(featplan, 8000)

    pipe = (decoder | aubio | yaaf | level)
    pipe.run()
#    print 'Pauses: %s' % str(decoder.pauses)
    return pipe


if __name__ == '__main__':
    #    fname = sys.argv[1]
    if len(sys.argv) > 1:
        nbuffs = int(sys.argv[1])
    else:
        nbuffs = 1000
    use_vad = len(sys.argv) > 2 and sys.argv[2].lower() == 'true'
    analyze_speech(nbuffs, use_vad)

