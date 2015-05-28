# analyze_speech.py

# Early version of public speech analysis/feedback software

from __future__ import division
import matplotlib.pylab as pylab
pylab.rcParams['figure.figsize'] = 16, 12  # that's default image size for this interactive session
import timeside
from timeside.core import get_processor

import matplotlib.pyplot as plt
import numpy as np
import sys, os

audiofile = sys.argv[1]
analysis_def = sys.argv[2]

# normal
file_decoder = get_processor('file_decoder')(audiofile, start=10, duration=20)
#e = timeside.encoder.VorbisEncoder('output.ogg', overwrite = True)
aubio_pitch = get_processor('aubio_pitch')()
aubio_temporal = get_processor('aubio_temporal')()
level = get_processor('level')()
specgram_ = get_processor('spectrogram_analyzer')()
waveform = get_processor('waveform_analyzer')()
#g  =  timeside.grapher.Spectrogram()

speech_decoder = get_processor('file_decoder')(audiofile, start=10, duration=20)
speech_decoder.output_blocksize=2048
irit4hz = get_processor('irit_speech_4hz')()
iritEntropy = get_processor('irit_speech_entropy')()
spspecgram_ = get_processor('spectrogram_analyzer')()

#print 'Pitch (etc.) results:\n'
#print pitchpipe.results.keys()

#print 'Speech segmentation results:\n'
#print '

if analysis_def == 'pitch':

    pitchpipe = (file_decoder | aubio_pitch | aubio_temporal | specgram_ | waveform)
    print 'Pitch pipe:\n'
    print pitchpipe
    pitchpipe.run()

    # Display Spectrogram + Aubio Pitch + Aubio Beat
    plt.figure(1)

    spec_res = specgram_.results['spectrogram_analyzer']
    N = spec_res.parameters['fft_size']
    plt.imshow(20 * np.log10(spec_res.data.T), origin='lower', extent=[spec_res.time[0],
               spec_res.time[-1], 0, (N // 2 + 1) / N * spec_res.data_object.frame_metadata.samplerate],
               aspect='auto')

    res_pitch = aubio_pitch.results['aubio_pitch.pitch']
    plt.plot(res_pitch.time, res_pitch.data)


    res_beats = aubio_temporal.results['aubio_temporal.beat']

    for time in res_beats.time:
        plt.axvline(time, color='r')

    plt.title('Spectrogram + Aubio pitch + Aubio beat')
    plt.grid()

    # Display waveform + Onsets
    plt.figure(2)
    res_wave = waveform.results['waveform_analyzer']
    plt.plot(res_wave.time, res_wave.data)
    res_onsets = aubio_temporal.results['aubio_temporal.onset']
    for time in res_onsets.time:
        plt.axvline(time, color='r')
        plt.grid()
        plt.title('Waveform + Aubio onset')
        plt.show()

    res_pitch.render()
    res_onsets.render()

elif analysis_def == 'speech':

    speechpipe = (speech_decoder | irit4hz | iritEntropy | spspecgram_).run()
    print 'Speech pipe:\n'
    print speechpipe
    
    irit_4hz_seg = irit4hz.results['irit_speech_4hz.segments']
    irit_4hz_seg_med = irit4hz.results['irit_speech_4hz.segments_median']
    irit_entropy_seg = iritEntropy.results['irit_speech_entropy.segments']

    irit_4hz_seg.render()
    irit_4hz_seg_med.render()

    plt.figure(1)

    spec_res = spspecgram_.results['spectrogram_analyzer']
    N = spec_res.parameters['fft_size']
    plt.imshow(20 * np.log10(spec_res.data.T+1e-2), origin='lower',
               extent=[spec_res.time[0], spec_res.time[-1], 0,
               (N // 2 + 1) / N * spec_res.data_object.frame_metadata.samplerate],
               aspect='auto', cmap = 'binary')

    for (time, dur, label) in zip(irit_4hz_seg.time, irit_4hz_seg.duration, irit_4hz_seg.data):
        if label == 0:
            pass
        #plt.axvspan(time, time+dur , color='g', alpha=0.4)
        elif label == 1:
            plt.axvspan(time, time+dur , color='b', alpha=0.3)

    plt.title('Spectrogram + 4Hz Seg')
    plt.axis('tight')
    plt.ylim( (0, 8000) )
    plt.grid()

    irit_entropy_seg.render()
    plt.show()

