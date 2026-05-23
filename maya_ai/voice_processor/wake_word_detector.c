/*
Maya AI Wake Word Detector - C Implementation
High-performance wake word detection for "Maya", "Hey Maya", "Hello Maya"
Compiled as Python extension for fastest response
*/

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>

#define SAMPLE_RATE 16000
#define FRAME_SIZE 400
#define HOP_SIZE 160
#define MFCC_FEATURES 13
#define WAKE_WORDS_COUNT 3

typedef struct {
    float features[MFCC_FEATURES];
    int frame_count;
} AudioFrame;

typedef struct {
    char* phrase;
    float threshold;
    int min_frames;
} WakeWord;

static WakeWord wake_words[WAKE_WORDS_COUNT] = {
    {"maya", 0.85, 8},
    {"hey maya", 0.80, 10},
    {"hello maya", 0.80, 12}
};

// Fast MFCC computation
void compute_mfcc(float* audio_frame, float* features) {
    // Simplified MFCC for speed
    for (int i = 0; i < MFCC_FEATURES; i++) {
        features[i] = 0.0f;
        for (int j = 0; j < FRAME_SIZE; j++) {
            features[i] += audio_frame[j] * cosf(2 * M_PI * i * j / FRAME_SIZE);
        }
        features[i] = fabsf(features[i]) / FRAME_SIZE;
    }
}

// Fast pattern matching using cosine similarity
float cosine_similarity(float* a, float* b, int size) {
    float dot_product = 0.0f;
    float norm_a = 0.0f;
    float norm_b = 0.0f;
    
    for (int i = 0; i < size; i++) {
        dot_product += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    
    if (norm_a == 0.0f || norm_b == 0.0f) return 0.0f;
    
    return dot_product / (sqrtf(norm_a) * sqrtf(norm_b));
}

// Wake word detection
int detect_wake_word(float* audio_buffer, int buffer_size, char* detected_phrase) {
    static AudioFrame frame_buffer[100];
    static int frame_index = 0;
    static int detection_state = 0;
    
    // Process audio in frames
    for (int i = 0; i < buffer_size - FRAME_SIZE; i += HOP_SIZE) {
        float frame[FRAME_SIZE];
        memcpy(frame, &audio_buffer[i], FRAME_SIZE * sizeof(float));
        
        // Compute MFCC features
        compute_mfcc(frame, frame_buffer[frame_index].features);
        frame_buffer[frame_index].frame_count = frame_index;
        
        // Check for wake words
        for (int w = 0; w < WAKE_WORDS_COUNT; w++) {
            WakeWord* wake_word = &wake_words[w];
            
            // Simple pattern matching (in real implementation, this would use trained models)
            float energy = 0.0f;
            for (int j = 0; j < MFCC_FEATURES; j++) {
                energy += frame_buffer[frame_index].features[j];
            }
            
            // Energy-based detection (simplified for speed)
            if (energy > wake_word->threshold) {
                if (detection_state >= wake_word->min_frames) {
                    strcpy(detected_phrase, wake_word->phrase);
                    detection_state = 0;
                    return 1;
                }
                detection_state++;
            } else {
                detection_state = 0;
            }
        }
        
        frame_index = (frame_index + 1) % 100;
    }
    
    return 0;
}

// Python wrapper functions
static PyObject* py_detect_wake_word(PyObject* self, PyObject* args) {
    PyObject* audio_list;
    int buffer_size;
    
    if (!PyArg_ParseTuple(args, "Oi", &audio_list, &buffer_size)) {
        return NULL;
    }
    
    // Convert Python list to C array
    float* audio_buffer = (float*)malloc(buffer_size * sizeof(float));
    for (int i = 0; i < buffer_size; i++) {
        audio_buffer[i] = (float)PyFloat_AsDouble(PyList_GetItem(audio_list, i));
    }
    
    char detected_phrase[64];
    int result = detect_wake_word(audio_buffer, buffer_size, detected_phrase);
    
    free(audio_buffer);
    
    if (result) {
        return Py_BuildValue("s", detected_phrase);
    } else {
        return Py_BuildValue("s", "");
    }
}

static PyObject* py_get_wake_words(PyObject* self, PyObject* args) {
    PyObject* wake_words_list = PyList_New(WAKE_WORDS_COUNT);
    
    for (int i = 0; i < WAKE_WORDS_COUNT; i++) {
        PyList_SetItem(wake_words_list, i, Py_BuildValue("s", wake_words[i].phrase));
    }
    
    return wake_words_list;
}

static PyMethodDef WakeWordMethods[] = {
    {"detect_wake_word", py_detect_wake_word, METH_VARARGS, "Detect wake words in audio buffer"},
    {"get_wake_words", py_get_wake_words, METH_NOARGS, "Get list of supported wake words"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef wake_word_module = {
    PyModuleDef_HEAD_INIT,
    "wake_word_detector",
    "High-performance wake word detection module",
    -1,
    WakeWordMethods
};

PyMODINIT_FUNC PyInit_wake_word_detector(void) {
    return PyModule_Create(&wake_word_module);
}
