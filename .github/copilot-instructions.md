# GPT-Rewind AI Coding Guidelines

## Project Overview
GPT-Rewind analyzes ChatGPT-like conversation data from JSON exports. It processes chat sessions to extract metrics on style, usage patterns, and temporal distributions. The core data structure is a list of sessions with nested message mappings containing fragments (REQUEST/THINK/RESPONSE types).

## Architecture
- **APIs** (`rewind/apis/`): High-level functions like `emoji_counts()`, `session_count()` that load JSON, process data, and return stats dicts/lists
- **Data Processing** (`rewind/data_process/`): Modular processors for loading (`load_json()`), updating (`update_data()` - extracts longest interaction chains), and computing metrics (style, numeric, time)
- **Utils** (`rewind/utils/`): Shared helpers for language detection (`chinese_dominant()`), data iteration (`iterate_fragments()`), time parsing (`delta_to_dhms()`), and ML models
- **Models** (`models/`): Local Hugging Face models for topic classification

## Key Patterns
- **Data Flow**: Always `load_json() -> update_data() -> specific_processor()` in APIs
- **Fragment Iteration**: Use `iterate_fragments(data_list)` to yield `(content, interaction_type)` for all message fragments
- **Stats Format**: Return dicts/lists with descriptive keys (e.g., `{"model": "gpt-4", "usage": 42}`)
- **Model Integration**: Load local models via `AutoTokenizer.from_pretrained("models/TopicClassifier-NoURL")`
- **Time Handling**: Parse ISO timestamps with `dateutil.parser.isoparse()`, calculate deltas with `delta_to_dhms()`

## Development Workflow
- **Linting**: Run `pylint rewind/ tests/` (configured in CI and pre-commit)
- **Dependencies**: Install from `requirements.txt` (includes transformers, bertopic, datasets)
- **Data**: Use `data/example.json` for testing; real data in `data/conversations.json` (gitignored)
- **Testing**: No tests yet - add unit tests in `tests/` for API functions with mock data

## Conventions
- Functions take `json_path: str` and return processed dicts/lists
- Use type hints (`List[Dict[str, Any]]`) for data structures
- Handle missing keys gracefully with `.get()` (e.g., `session.get("title", "unknown")`)
- Process only RESPONSE/THINK fragments for AI-generated content, REQUEST for user input
- Language detection prioritizes Chinese vs English character counts

## Examples
- Add new metric: Create processor in `data_process/`, import in `base_api.py`, follow `load_json() -> update_data() -> processor()` pattern
- Time analysis: Use `chat_frequency_distribution()` for monthly/daily counts from `inserted_at` timestamps
- Style analysis: Count emojis/politeness only in AI responses using `iterate_fragments()` with type filtering</content>
<parameter name="filePath">/Users/bytedance/Desktop/code/research/GPT-Rewind/.github/copilot-instructions.md