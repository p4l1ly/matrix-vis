import base64
from io import BytesIO

import numpy as np
import yaml

matrix = np.array([
    [
        [
            [1, 2, 3],
            [3, 2, 3],
            [3, 2, 2],
        ],
        [
            [5, 2, 1],
            [3, 2, 4],
            [4, 7, 2],
        ]
    ],
    [
        [
            [1, 7, 2],
            [1, 2, 5],
            [3, 3, 3],
        ],
        [
            [5, 2, 9],
            [3, 0, 3],
            [5, 9, 5],
        ]
    ]
])

file = BytesIO()
np.save(file, matrix)

result = yaml.dump({
    'info': 'This is a useless example',
    'dimensions': {
        'x': [3, 5],
        'hellofoobar': [0, 1],
        'z': [1, 2, 3],
        'a': ['foo', 'bar', 'baz']
    },
    'matrix': base64.b64encode(file.getvalue()).decode('ascii')
}, sort_keys=False)

print(result)