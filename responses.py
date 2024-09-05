from random import choice, randint

def get_response(user_input: str) -> str:
   lowered: str = user_input.lower()


   if lowered == '':
       return 'Well, you\'re awfully silent...'
   elif 'hello' in lowered:
       return 'Hello there!'
   elif 'how are you' in lowered:
       return 'Good, thanks!'
   elif 'bye' in lowered:
       return 'See you!'
   elif 'roll dice' in lowered:
       return f'You rolled: {randint(1, 6)}'
   elif 'cfa' in lowered:
       return (f'Click [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to open on ios')
   else:
       return choice(['I do not understand...',
                      'What are you talking about?',
                      'Do you mind rephrasing that?'])