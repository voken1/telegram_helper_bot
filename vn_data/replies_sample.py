# coding:utf-8

# welcome
hello = {
    'en': 'TEXT',
    'cn': 'TEXT',
}
hello2all = {
    'en': 'TEXT',
    'cn': 'TEXT',
}

# summaries
summaries = {
    'en': [
        'TEXT',
    ],
    'cn': [
        'TEXT',
    ],
}

# strictly, orderly, disorderly
rules = [
    {
        'title': 'vpn',
        'matching': [
            {
                'mode': 'orderly',
                'keys': [
                    ['hello there'],
                ],
            },
        ],
        'replies': {
            'en': [
                'hello test...',
            ],
            'cn': [
                'hello test...'
            ],
        },
    },
]
