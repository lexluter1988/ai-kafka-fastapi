OPENAI_COMPLETION_REQUEST_EXAMPLE = {
    'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
    'prompt': '<|im_start|>user\nTell me a short story about AI.<|im_end|>\n<|im_start|>assistant\n',  # noqa: E501
    'max_tokens': 100,
    'stream': True,
}

OPENAI_COMPLETION_RESPONSE_EXAMPLE = {
    'id': 'cmpl-328a1c081c3b46a984d51786e1475f0e',
    'object': 'text_completion',
    'created': 1741345397,
    'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
    'choices': [
        {
            'index': 0,
            'text': ' integrate',
            'logprobs': None,
            'finish_reason': None,
            'stop_reason': None,
        }
    ],
    'usage': None,
}

OPENAI_CHAT_COMPLETION_REQUEST_EXAMPLE = {
    'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
    'messages': [
        {'role': 'system', 'content': 'Ты помощник.'},
        {'role': 'user', 'content': 'Привет, как дела?'},
    ],
    'temperature': 0.7,
}


OPENAI_CHAT_COMPLETION_RESPONSE_EXAMPLE = {
    'id': 'chatcmpl-e89f417d58b747639cb167ceeabd4b2e',
    'object': 'chat.completion',
    'created': 1741347095,
    'model': 'Qwen/Qwen2.5-72B-Instruct-AWQ',
    'choices': [
        {
            'index': 0,
            'message': {
                'role': 'assistant',
                'reasoning_content': None,
                'content': 'Привет! У меня всё хорошо, спасибо. Как у тебя дела? Чем могу помочь?',
                'tool_calls': [],
            },
            'logprobs': None,
            'finish_reason': 'stop',
            'stop_reason': None,
        }
    ],
    'usage': {
        'prompt_tokens': 25,
        'total_tokens': 52,
        'completion_tokens': 27,
        'prompt_tokens_details': None,
    },
    'prompt_logprobs': None,
}
