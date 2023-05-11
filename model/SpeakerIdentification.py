import os
import pickle
import warnings
import numpy as np
from sklearn import preprocessing
from scipy.io.wavfile import read
import python_speech_features as mfcc
from sklearn.mixture import GaussianMixture
from src.s3 import download_from_s3, uplaodtoS3

warnings.filterwarnings("ignore")




def calculate_delta(array):

    rows, cols = array.shape
    print(rows)
    print(cols)
    deltas = np.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i-j < 0:
                first = 0
            else:
                first = i-j
            if i+j > rows-1:
                second = rows-1
            else:
                second = i+j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]]-array[index[0][1]] +
                     (2 * (array[index[1][0]]-array[index[1][1]]))) / 10
    return deltas


def extract_features(audio, rate):

    mfcc_feature = mfcc.mfcc(audio, rate, 0.025, 0.01,
                             20, nfft=1200, appendEnergy=True)
    mfcc_feature = preprocessing.scale(mfcc_feature)
    print(mfcc_feature)
    delta = calculate_delta(mfcc_feature)
    combined = np.hstack((mfcc_feature, delta))
    return combined

def train_model():
    train_file = []
    file_list = download_from_s3("model/training_set/")
    for file in file_list:
        train_file.append(file.split("/")[-1])

    models_folder = "trained_models"
    features = np.asarray(())

    count = 1
    for path in train_file:
        print(path)

        file = download_from_s3("model/training_set/" + path)
        sr, audio = read(file)
        print(sr)
        vector = extract_features(audio, sr)

        if features.size == 0:
            features = vector
        else:
            features = np.vstack((features, vector))

        if count == 1:
            gmm = GaussianMixture(
                n_components=6, max_iter=200, covariance_type='diag', n_init=3)
            gmm.fit(features)

            # dumping the trained gaussian model
            picklefile = path.split("-")[0] + ".gmm"
            with open(picklefile, 'wb') as f:
                pickle.dump(gmm, f)
            s3_key = models_folder + picklefile
            with open(picklefile, 'rb') as f:
                uplaodtoS3(models_folder, s3_key, f)
            print('+ modeling completed for speaker:', picklefile,
                  " with data point = ", features.shape)
            features = np.asarray(())
            count = 0
        count = count + 1

def test_model():
    test_file = []
    file_list = download_from_s3("model/testing_set/")
    for file in file_list:
        test_file.append(file.split("/")[-1])

    source = "model/testing_set/"
    modelpath = "model/trained_models/"

    gmm_files = []
    for fname in download_from_s3(modelpath):
        if fname.endswith('.gmm'):
            gmm_files.append(fname.split("/")[-1])

    # Load the Gaussian gender Models
    models = []
    speakers = []
    for fname in gmm_files:
        file = download_from_s3(modelpath + fname)
        models.append(pickle.load(open(file, 'rb')))
        speakers.append(fname.split(".gmm")[0])

    winner = ''
    # Read the test directory and get the list of test audio files
    for path in test_file:

        path = path.strip()
        print(path)
        file = download_from_s3("model/testing_set/" + path)
        sr, audio = read(file)
        vector = extract_features(audio, sr)

        log_likelihood = np.zeros(len(models))

        for i in range(len(models)):
            gmm = models[i]  # checking with each model one by one
            scores = np.array(gmm.score(vector))
            log_likelihood[i] = scores.sum()

        winner = np.argmax(log_likelihood)
        print("\tdetected as - ", speakers[winner])
    return speakers[winner]

# choice=int(input("\n1.Record audio for training \n 2.Train Model \n 3.Record audio for testing \n 4.Test Model\n"))




