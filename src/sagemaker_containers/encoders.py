# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import

import json
import textwrap

import numpy as np
from six import BytesIO, StringIO

from sagemaker_containers import content_types


def array_to_npy(array_like):  # type: (np.array or Iterable or int or float) -> object
    """Convert an array like object to the NPY format.

    To understand better what an array like object is see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays

    Args:
        array_like (np.array or Iterable or int or float): array like object to be converted to NPY.

    Returns:
        (obj): NPY array.
    """
    buffer = BytesIO()
    np.save(buffer, array_like)
    return buffer.getvalue()


def npy_to_numpy(npy_array):  # type: (object) -> np.array
    """Convert an NPY array into numpy.

    Args:
        npy_array (npy array): to be converted to numpy array

    Returns:
        (np.array): converted numpy array.
    """
    stream = BytesIO(npy_array)
    return np.load(stream)


def array_to_json(array_like):  # type: (np.array or Iterable or int or float) -> str
    """Convert an array like object to JSON.

    To understand better what an array like object is see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays

    Args:
        array_like (np.array or Iterable or int or float): array like object to be converted to JSON.

    Returns:
        (str): object serialized to JSON
    """

    def default(_array_like):
        if hasattr(_array_like, 'tolist'):
            return _array_like.tolist()
        return json.JSONEncoder().default(_array_like)

    return json.dumps(array_like, default=default)


def json_to_numpy(string):  # type: (object) -> np.array
    """Convert a JSON object to a numpy array.

        Args:
            string (str): JSON string.

        Returns:
            (np.array): numpy array
        """
    data = json.loads(string)
    return np.array(data)


def csv_to_numpy(string):  # type: (str) -> np.array
    """Convert a CSV object to a numpy array.

    Args:
        string (str): CSV string.

    Returns:
        (np.array): numpy array
    """
    stream = StringIO(string)
    return np.genfromtxt(stream, dtype=np.float32, delimiter=',')


def array_to_csv(array_like):  # type: (np.array or Iterable or int or float) -> str
    """Convert an array like object to CSV.

    To understand better what an array like object is see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays

    Args:
        array_like (np.array or Iterable or int or float): array like object to be converted to CSV.

    Returns:
        (str): object serialized to CSV
    """
    stream = StringIO()
    np.savetxt(stream, array_like, delimiter=',', fmt='%s')
    return stream.getvalue()


_encoders_map = {content_types.NPY: array_to_npy, content_types.CSV: array_to_csv, content_types.JSON: array_to_json}
_decoders_map = {content_types.NPY: npy_to_numpy, content_types.CSV: csv_to_numpy, content_types.JSON: json_to_numpy}


def decode(obj, content_type):  # type: (np.array or Iterable or int or float) -> np.array
    """Decode an object ton a one of the default content types to a numpy array.

    Args:
        obj (object): to be decoded.
        content_type (str): content type to be used.

    Returns:
        object: decoded object.
    """
    try:
        decoder = _decoders_map[content_type]
        return decoder(obj)
    except KeyError:
        raise UnsupportedFormatError(content_type)


def encode(array_like, content_type):  # type: (np.array or Iterable or int or float) -> np.array
    """Encode an array like object in a specific content_type to a numpy array.

    To understand better what an array like object is see:
    https://docs.scipy.org/doc/numpy/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays

    Args:
        array_like (np.array or Iterable or int or float): to be converted to numpy.
        content_type (str): content type to be used.

    Returns:
        (np.array): object converted as numpy array.
    """
    try:
        encoder = _encoders_map[content_type]
        return encoder(array_like)
    except KeyError:
        raise UnsupportedFormatError(content_type)


class UnsupportedFormatError(Exception):
    def __init__(self, content_type, **kwargs):
        super(Exception, self).__init__(**kwargs)
        self.message = textwrap.dedent(
            """Content type %s is not supported by this framework.

               Please implement input_fn to to deserialize the request data or an output_fn to serialize the
               response. For more information: https://github.com/aws/sagemaker-python-sdk#input-processing"""
            % content_type)
