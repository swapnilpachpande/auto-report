class AiSummary:
    def __init__(self, model):
        self.model = model  # LLM instance

    @classmethod
    def get_ai_model(cls, api_key: str = None, model_name: str = 'gpt-3.5-turbo', max_tokens: int = 1500, temperature: float = 0.0):
        """
        Create a callable wrapper around the installed OpenAI client (new-style or legacy).

        The returned object's `model` attribute is a callable that accepts a single
        `prompt: str` argument and returns whatever the underlying SDK returns.

        :param api_key: Optional OpenAI API key. If omitted, the SDK will use env vars.
        :param model_name: Model name to request (default: 'gpt-3.5-turbo').
        :param max_tokens: Max tokens for the completion call.
        :param temperature: Sampling temperature.
        :return: AiSummary instance with .model callable.
        :raises ImportError: if the OpenAI SDK isn't installed.
        """
        try:
            import openai
        except Exception as e:
            raise ImportError('OpenAI SDK not installed. Install with `pip install openai` or provide a custom model callable.') from e

        # New-style OpenAI client present in recent SDKs
        if hasattr(openai, 'OpenAI'):
            client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()

            def model_callable(prompt: str):
                return client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
        else:
            # Legacy `openai` module
            if api_key:
                openai.api_key = api_key

            def model_callable(prompt: str):
                return openai.ChatCompletion.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

        return cls(model_callable)

    def generate_ai_summary(self, csv_data, context=None):
        """
        Generate the ai summary report of any CSV dataset.
        
        :param csv_data: stringified summary of the csv data
        :param context: optional dict, containing additional analysis parameters or requirements
                       e.g., {'focus_columns': ['col1', 'col2'], 'target_variable': 'target'}
        :return: str, ai summary report
        """
        # Build the prompt for the AI model
        prompt_parts = [
            "You are a data analyst.",
            "Given the following CSV summary/data, provide a concise, clear analysis and actionable insights.",
            "CSV Data Summary:",
            csv_data
        ]
        
        # Add any additional context
        if context:
            prompt_parts.extend(["", "Additional Analysis Context:"])
            if isinstance(context, dict):
                for k, v in context.items():
                    prompt_parts.append(f"- {k}: {v}")
            else:
                prompt_parts.append(str(context))
        
        # Final instructions for the model
        prompt = "\n".join(prompt_parts)
        print('-----------------------Prompt--------------------------------')
        print(prompt)
        print('-------------------------------------------------------')
        # Try calling the model and be tolerant of a few common response shapes.
        max_retries = 2
        last_exc = None
        for attempt in range(max_retries):
            try:
                response = None
                # Common interfaces
                if hasattr(self.model, 'complete'):
                    # simple wrapper-style API
                    response = self.model.complete(prompt)
                elif hasattr(self.model, 'generate'):
                    response = self.model.generate(prompt)
                elif callable(self.model):
                    response = self.model(prompt)
                else:
                    raise RuntimeError('Unsupported model interface: provide .complete, .generate, or a callable')

                # Extract textual content from OpenAI ChatCompletion response
                report = None

                # New-style OpenAI client (response is ChatCompletion object)
                if hasattr(response, 'choices') and hasattr(response.choices[0], 'message'):
                    report = response.choices[0].message.content
                # Legacy dict-style response
                elif isinstance(response, dict) and 'choices' in response:
                    message = response['choices'][0].get('message', {})
                    report = message.get('content')
                # Fallback for other response types
                elif hasattr(response, 'text'):
                    report = response.text
                else:
                    report = str(response)

                if report is None:
                    raise ValueError('Model response did not contain extractable text')

                # Trim and return the text
                return report.strip()
            except Exception as e:
                last_exc = e
                # small backoff could be added here
                continue

        # If we reach here, model calls failed — return Null
        print(f"\nLLM call failed after {max_retries} attempts: {last_exc}")
        return None
