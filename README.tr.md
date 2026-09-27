# Deep Research Companion (Kanıt Hattı)

[English](README.md) | Türkçe

**Perplexity, ChatGPT ya da Gemini ile araştır ve hangi bilginin gerçekten doğru olduğunu bil.**

Yapay zekâ arama araçları kendinden emin cevaplar ve kaynaklar verir. Bazı kaynaklar cevabın söylediğini söylemez, bazıları hiç yoktur. Deep Research Companion, zaten kullandığın arama aracının yanında çalışan bir ajan skill'idir. Promptu yazar, gelen cevabı iddia iddia kaynağından kontrol eder. Büyük sorularda ise sonunda iki belge çıkaran tam bir araştırma yürütür: tam araştırma ve özet.

Konu fark etmez: tarih, sağlık, bilim, hukuk, müzik, pazar. Sorular skill'den değil, senin konundan çıkar. Yöntemin Türkçe adı **Kanıt Hattı**.

## Örnek

Gerçek bir test çalıştırması. Skill'e Apollo 11 hakkında, Perplexity tarzında bir cevap verdik. İçine bilerek bir yanlış bilgi ve bir uydurma bağlantı koyduk ([answer.tr.md](examples/apollo-11/answer.tr.md)):

> Apollo 11 görevi 16 Temmuz 1969'da Florida'daki Kennedy Uzay Merkezi'nden fırlatıldı [1]. Ay'a iniş 20 Temmuz 1969'da gerçekleşti [1]. Neil Armstrong ve Buzz Aldrin Ay yüzeyinde yürürken Michael Collins yörüngede kaldı [2]. Ay modülünün adı Columbia'ydı [2]. Astronotlar Ay yüzeyinde yaklaşık 21,5 saat kaldı [3]. Görev 24 Temmuz 1969'da Pasifik Okyanusu'na inişle sona erdi [1].

**Sen sorarsın:** "Bu doğru mu?"

**Skill cevaplar** (kısaltıldı; tamamı [check.tr.md](examples/apollo-11/check.tr.md) dosyasında):

> 9 iddia: 8 doğrulandı, 1 yanlış, 0 bulunamadı; bağlantılar: 2/3 açıldı (3. bağlantı açılmıyor, büyük olasılıkla uydurma).

| No | İddia | Etiket | Not |
|---|---|---|---|
| 6 | Ay modülünün adı Columbia'ydı | [Y] | Yanlış. Ay modülünün adı **Eagle**; Columbia komuta modülünün adı. Cevabın kendi kaynağı da böyle yazıyor. |
| 7 | Ay yüzeyinde yaklaşık 21,5 saat kalındı | [D] | Doğru (21 sa 36 dk), ama gösterilen PDF 404 veriyor ve böyle bir belge bulunamadı: büyük olasılıkla uydurma. Yerine NASA kaynağı kondu. |
| 9 | Dönüş inişi Pasifik Okyanusu'na yapıldı | [D] | Doğru, ama gösterilen NASA sayfasında yazmıyor: atıf hatası. |

Bilerek konan yanlışı ve uydurma bağlantıyı yakaladı; kimsenin koymadığı bir atıf hatasını da buldu. Ayrıca çalışan kaynaklarla düzeltilmiş bir sürüm verdi.

## Üç bölüm

| Bölüm | Sen ne dersin | Ne alırsın |
|---|---|---|
| **Prompt yazma** | "Beatles'ın neden dağıldığını Perplexity'ye nasıl sorayım?" | Amacına dair 2–3 soru, ardından birincil kaynak isteyen, bulamadığında tahmin yerine "bulunamadı" diyen ve kaynak listesiyle biten, yapıştırmaya hazır tek bir prompt; ayrıca takip promptları |
| **Cevap doğrulama** | "Bu cevap doğru mu?" ve cevap | Her iddia kaynağından kontrol edilir: sonuç tablosu, ölü bağlantı raporu ve düzeltilmiş sürüm; istenirse DOCX ya da PDF |
| **Büyük araştırma** | "X'i düzgünce araştıralım" | Seninle kurulan bir plan, aracına yapıştırılacak koşular, önemli bulguların doğrulanması ve iki belge: tam araştırma ve özet (DOCX, PDF ya da ikisi) |

## Kurulum

Nerede çalışıyorsan onu seç. Ajan araçlarında üç bölümün hepsi çalışır. Sohbet uygulamalarında prompt yazma ve cevap doğrulama çalışır; büyük araştırma dosya ve script gerektirdiği için orada yoktur.

**Ajan araçları (üç bölüm)**

| Araç | Kurulum |
|---|---|
| Claude Code | `npx skills add dogancoban/deep-research-companion -g -a claude-code` |
| Claude Code, eklenti olarak | `/plugin marketplace add dogancoban/deep-research-companion`, sonra `/plugin install deep-research-companion@deep-research-companion` |
| Codex (OpenAI) | `npx skills add dogancoban/deep-research-companion -g -a codex` |
| Antigravity CLI (Google'ın Gemini CLI yerine çıkardığı araç) | `npx skills add dogancoban/deep-research-companion -g -a antigravity-cli` |
| Gemini CLI (Google'ın kurumsal lisanslarında hâlâ var) | `gemini skills install https://github.com/dogancoban/deep-research-companion.git --path skills/deep-research-companion` |
| Diğer [Agent Skills](https://agentskills.io) araçları | `npx skills add dogancoban/deep-research-companion -g`, sonra aracını seç |

Elle: `skills/deep-research-companion/` klasörünü aracının skill klasörüne kopyala (Claude Code: `~/.claude/skills/`).

**Sohbet uygulamaları (prompt yazma ve cevap doğrulama)**

| Uygulama | Kurulum |
|---|---|
| ChatGPT | Bir Proje aç ya da özel bir GPT oluştur. [chat-apps/instructions.md](chat-apps/instructions.md) dosyasını talimatlarına yapıştır ve web aramasını aç. |
| ChatGPT kurumsal (Business, Enterprise, Edu) | [Releases](https://github.com/dogancoban/deep-research-companion/releases/latest) sayfasından `deep-research-companion.zip` dosyasını indir ve skill olarak yükle (Skills → Create → Upload). |
| Gemini | Bir Gem oluştur ve [chat-apps/instructions.md](chat-apps/instructions.md) dosyasını talimatlarına yapıştır. |
| claude.ai | [Releases](https://github.com/dogancoban/deep-research-companion/releases/latest) sayfasındaki `deep-research-companion.zip` dosyasını Settings → Capabilities → Skills bölümünden yükle. |

Sonra konuşman yeterli:
- "James Webb teleskobunun ötegezegenleri nasıl bulduğunu araştırmama yardım et."
- "Bu üç koşu ayakkabısını karşılaştırmak için Perplexity'ye ne yazayım?"
- "Bu cevap doğru mu?" (cevabı kaynaklarıyla birlikte yapıştır)

## Etiketler

Her bulgunun yanında bir etiket durur; belgelerde renklidir. Türkçe belgeler Türkçe etiketleri kullanır:

| Etiket | Anlamı |
|---|---|
| [D] | Doğrulandı: birincil kaynak açıldı ve bunu söylüyor |
| [K] | Kaynaklı: kaynak gösterilmiş ama açılmadı |
| [İ] | İkincil: yalnızca ikincil kaynaklarda var |
| [Ç] | Çelişki: kaynaklar farklı şey söylüyor |
| [Y] | Yanlış: birincil kaynak başka bir şey söylüyor |
| [B] | Bulunamadı: gösterilen kaynakta yok, başka yerde de bulunamadı |

İngilizce belgeler [V] [U] [S] [C] [W] [N] kullanır.

## Gerekenler

- **Prompt yazma ve cevap doğrulama:** Ek bir şey gerekmez. Bağlantı kontrolü için Python 3 ve curl yeter; ikisi de macOS'ta ve çoğu Linux'ta hazır gelir.
- **Büyük araştırma:** Python 3.
- **DOCX ve PDF belgeler:** Node.js 18+, LibreOffice ve Poppler. macOS'ta: `brew install node poppler && brew install --cask libreoffice`.

## Diller

Skill seninle senin dilinde konuşur; promptları ve belgeleri de senin dilinde yazar. En iyi kaynaklar başka bir dildeyse, prompt arama aracına o dilde de aramasını söyler. Belgelerin İngilizce ve Türkçe düzeni var; diğer diller İngilizce düzeni kullanır. Klasör ve dosya adları İngilizcedir.

## Nasıl çalışır

- **Arama aracı toplar, asistanın doğrular.** Arama araçları kaynak bulmakta hızlı, kaynağı doğru aktarmakta güvenilmezdir. Skill'i çalıştıran asistan (Claude, ChatGPT, Gemini…) kaynakları açar ve gerçekte ne yazdığına bakar.
- **Büyük araştırma sabit kurallarla ilerler.** Her koşu aynı kuralları (bir "anayasa") taşır, sorular bir kapsam listesinde izlenir ve diğerlerinden önce tek bir pilot koşu kontrol edilir.
- **Sonda yeni bilgi eklenmez.** Belgelere yalnızca toplanmış ve etiketlenmiş bulgular girer. Asistanın kendi çıkarımları "Değerlendirme" diye işaretlenir.
- **Konudan bağımsızdır.** Skill'de hazır konu listesi yoktur. Soruları, kaynak sırasını ve neyin kaydedileceğini senin konundan ve amacından çıkarır.

## Durum ve sınırlar

- **Test edilenler:** macOS'ta Claude Code ile üç bölüm, scriptler, DOCX ve PDF üretimi. Sohbet sürümü ChatGPT ve Gemini uygulamalarında Apollo örneğiyle test edildi: ikisi de yanlış bilgiyi yakaladı ve açılmayan bağlantıyı kaynak göstermek yerine raporladı.
- **Sohbet sürümünün sınırı:** Bu testlerde iki uygulama da atıf hatasını kaçırdı (doğru bir bilginin gösterilen sayfada yazmaması). Kaynakları scriptlerle açıp içinde arayan ajan sürümü bunu her testte yakaladı.
- **Henüz test edilmeyenler:** Codex, Antigravity CLI, Gemini CLI ve claude.ai. Hepsi aynı açık skill biçimini okuduğu için çalışması beklenir; geri bildirim memnuniyetle karşılanır.
- Büyük araştırma zaten ödediğin aracı kullanır. Koşu promptlarını kendin yapıştırır, cevapları geri getirirsin; API anahtarı gerekmez.
- Kontrol, açılabilen kaynaklar kadar iyidir. Ücretli ya da erişimi engellenmiş sayfalar [K] olarak kalır.

## Teşekkür

Fikirler kopyalanmadan uyarlandı: [claude-skill-perplexity-prompting](https://github.com/joelhelbling/claude-skill-perplexity-prompting), fact-check skill'leri ve [academic-research-skills](https://github.com/Imbad0202/academic-research-skills) içindeki atıf kontrolleri.

## Lisans

[MIT](LICENSE)
