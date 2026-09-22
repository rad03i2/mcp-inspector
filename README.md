# MCP Inspector Local

A small, local-first Python CLI for inspecting **Model Context Protocol (MCP) client configuration files without starting the configured servers**. It helps developers catch structural mistakes, inventory transports, flag risky inline secrets, and produce a reviewable redacted copy.

> The project validates configuration shape and safety signals. It is not the official MCP Inspector and it does not claim protocol conformance testing.

## Why it exists
MCP client configurations often mix executable commands, arguments, environment names, remote URLs, and credentials. Reviewing them by eye is error-prone, while launching an unknown server just to inspect its configuration is undesirable. This tool deliberately stays offline and non-executing.

## Features
- Validates the top-level `mcpServers` map and each server definition.
- Recognizes stdio-style `command` servers and HTTP(S) `url` servers.
- Validates string argument arrays and environment-variable names/values.
- Warns about unencrypted remote HTTP endpoints.
- Warns when likely credentials appear inline in environment values.
- Produces a safe inventory containing environment **names**, never environment values.
- Redacts likely secret environment values plus common authentication headers.
- Deterministic text and JSON output suitable for CI.
- Exit codes: `0` valid, `1` validation errors found, `2` input/I/O error.
- Python API with no runtime dependencies beyond the standard library.

## Preview
```text
$ mcp-inspector-local check examples/mcp.example.json
MCP servers: 2
- local-tools: stdio (enabled)
- remote-example: http (enabled)
Findings: 0 error(s), 0 warning(s), 0 info
```

For screenshots, run the command in your preferred terminal; this repository intentionally does not ship generated screenshots that could become stale.

## Requirements & installation
- Python 3.10+

```bash
git clone https://github.com/rad03i2/mcp-inspector.git
cd mcp-inspector
python -m pip install -e .
```

## Usage
```bash
# Human-readable validation
mcp-inspector-local check path/to/mcp.json

# Machine-readable result
mcp-inspector-local check path/to/mcp.json --json

# Inventory servers without exposing env values
mcp-inspector-local summary path/to/mcp.json

# Create a review copy with likely secrets removed
mcp-inspector-local redact path/to/mcp.json --output safe-review.json

# Module form
python -m mcp_inspector check examples/mcp.example.json
```

A minimal configuration:
```json
{
  "mcpServers": {
    "local-tools": {
      "command": "python",
      "args": ["-m", "my_mcp_server"],
      "env": {"API_TOKEN": "${API_TOKEN}"}
    }
  }
}
```

The inspector accepts a few common client keys (`cwd`, `headers`, `disabled`) and reports other keys as informational rather than deleting or rewriting them.

## Python API
```python
from mcp_inspector import load_config, summary

report = summary(load_config("mcp.json"))
print(report["finding_counts"])
```

## Configuration
The tool itself requires no environment variables, network access, account, API key, or `.env` file. Input is UTF-8 JSON. It never resolves `${...}` placeholders because doing so could expose secrets.

## Project structure
```text
src/mcp_inspector/     core validator, redaction, CLI
examples/              synthetic safe example
tests/                 unit and CLI tests
.github/workflows/     cross-platform CI
SECURITY.md             security model
CONTRIBUTING.md         contribution guide
```

## Testing
```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
mcp-inspector-local check examples/mcp.example.json --json
```
CI runs these checks on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Security & privacy
Inspection is passive: configured commands are never executed and URLs are never contacted. `check` and `summary` do not emit environment values. Redaction is heuristic; always manually review a redacted file before sharing it because a credential may use an unusual key name. See [SECURITY.md](SECURITY.md).

## Limitations
- JSON configuration only; YAML/TOML are not parsed.
- Validation targets common MCP client configuration conventions, not every client-specific extension.
- It does not connect to servers, enumerate tools/resources/prompts, perform handshakes, or certify MCP protocol compliance.
- Redaction cannot identify every possible secret name or secret embedded inside arbitrary arguments/URLs.
- It does not check whether a command exists on `PATH` or whether a URL is reachable; those checks would move beyond passive inspection.

## Optional roadmap
Future work may add opt-in JSON Schema validation and explicit adapters for documented client formats while preserving the no-execution default.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes deterministic, tested, and free of real credentials.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## نظرة عامة
**MCP Inspector Local** أداة محلية مكتوبة ببايثون لفحص ملفات إعداد عملاء **Model Context Protocol (MCP)** من دون تشغيل الخوادم المعرفة داخل الملف. تساعد على اكتشاف أخطاء البنية، ومعرفة نوع الاتصال لكل خادم، والتنبيه إلى الأسرار المكتوبة مباشرة، وإنشاء نسخة منقحة قابلة للمراجعة.

> المشروع ليس الأداة الرسمية المسماة MCP Inspector ولا يدّعي اختبار التوافق الكامل مع البروتوكول.

## لماذا هذا المشروع؟
ملفات MCP قد تجمع أوامر تشغيل ومعاملات ومتغيرات بيئة وروابط بعيدة وبيانات اعتماد. تشغيل خادم غير معروف لمجرد فهم الإعداد ليس مناسبًا، لذلك صُممت هذه الأداة لتبقى سلبية: تقرأ JSON فقط ولا تنفذ الأوامر ولا تتصل بالروابط.

## الميزات
- التحقق من `mcpServers` وتعريف كل خادم.
- التعرف على خوادم `command` المحلية وروابط HTTP/HTTPS.
- فحص `args` وأسماء وقيم متغيرات البيئة بنيويًا.
- التحذير من HTTP البعيد غير المشفر.
- التحذير من القيم التي تبدو كأسرار مكتوبة مباشرة.
- ملخص لا يعرض قيم متغيرات البيئة مطلقًا.
- تنقيح القيم السرية المحتملة وترويسات المصادقة الشائعة.
- إخراج نصي أو JSON مناسب للأتمتة وCI.
- رموز خروج واضحة: `0` صالح، `1` أخطاء تحقق، `2` خطأ ملف/إدخال.
- API لبايثون بلا تبعيات تشغيل خارج المكتبة القياسية.

## المعاينة
```text
mcp-inspector-local check examples/mcp.example.json
```
لإنشاء لقطة شاشة حديثة شغّل الأمر في الطرفية؛ لا نخزن صورًا مولدة قد تصبح قديمة.

## المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث:
```bash
git clone https://github.com/rad03i2/mcp-inspector.git
cd mcp-inspector
python -m pip install -e .
```

## الاستخدام
```bash
mcp-inspector-local check path/to/mcp.json
mcp-inspector-local check path/to/mcp.json --json
mcp-inspector-local summary path/to/mcp.json
mcp-inspector-local redact path/to/mcp.json --output safe-review.json
python -m mcp_inspector check examples/mcp.example.json
```

## الإعداد
الأداة نفسها لا تحتاج مفتاح API أو حسابًا أو اتصال شبكة أو ملف `.env`. المدخل UTF-8 JSON. ولا تقوم بحل `${...}` لأن ذلك قد يكشف الأسرار.

## Python API
```python
from mcp_inspector import load_config, summary
report = summary(load_config("mcp.json"))
```

## بنية المشروع
`src/mcp_inspector/` للمحرك وCLI، و`tests/` للاختبارات، و`examples/` للمثال الآمن، و`.github/workflows/` للتكامل المستمر.

## الاختبارات
```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
mcp-inspector-local check examples/mcp.example.json --json
```
يشغّل CI الاختبارات على Ubuntu وWindows وmacOS مع Python 3.10 و3.12 و3.13.

## الأمان والخصوصية
لا تُشغّل الأداة أي أمر موجود في الإعداد ولا تتصل بأي URL. أوامر الفحص والملخص لا تعرض قيم متغيرات البيئة. التنقيح استدلالي وليس ضمانًا؛ راجع النسخة المنقحة يدويًا قبل مشاركتها، خصوصًا عند استخدام أسماء غير مألوفة للأسرار. راجع [SECURITY.md](SECURITY.md).

## القيود
- يدعم JSON فقط حاليًا.
- يستهدف الأنماط الشائعة لإعداد MCP وقد توجد امتدادات خاصة ببعض العملاء.
- لا يتصل بالخادم ولا يسرد الأدوات أو الموارد أو prompts ولا يجري handshake ولا يمنح شهادة توافق للبروتوكول.
- قد لا يتعرف التنقيح على سر ذي اسم غير معتاد أو سر موجود داخل argument أو URL.
- لا يفحص وجود الأمر في PATH ولا وصول الرابط لأن التصميم افتراضيًا سلبي وآمن.

## تطوير اختياري
يمكن مستقبلًا إضافة JSON Schema واختيارات صريحة لصيغ عملاء موثقة مع الحفاظ على مبدأ عدم التنفيذ افتراضيًا.

## المساهمة
راجع [CONTRIBUTING.md](CONTRIBUTING.md). يجب أن تبقى التغييرات قابلة للاختبار ومن دون بيانات اعتماد حقيقية.

## الترخيص
MIT — راجع [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
