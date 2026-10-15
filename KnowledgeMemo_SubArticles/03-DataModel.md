<!-- 本檔為 vChewing-DevLogs/KnowledgeMemo4LLM.md 之分卷；索引：../KnowledgeMemo4LLM.md
     開工前請先讀索引，再依〈三、任務→必讀分卷〉取用本檔。 -->

# 三、核心資料模型

| 型別 | 模組 | 用途 |
|------|------|------|
| `Homa.Gram` | Homa | 元圖單位（Unigram/Bigram），承載讀音、字詞、機率、前驗詞 |
| `Homa.Node` | Homa | 組字節點，含元圖陣列、覆寫狀態、Bigram 快取 |
| `Homa.Segment` | Homa | 字詞幅節，`[Int: Node]` 字典（鍵為幅節長度） |
| `Homa.Assembler` | Homa | 組字核心處理器，持有遊標、段落、配置、動態規劃演算法 |
| `VanguardTrie.Trie.TNode` | TrieKit | Trie 節點，含 id / readingKey / children / entries |
| `VanguardTrie.Trie.Entry` | TrieKit | Trie 詞條，含 value / typeID / probability / previous |
| `Tekkon.Phonabet` | Tekkon | 單注音符號（Unicode Scalar + PhoneType） |
| `Tekkon.Composer` | Tekkon | 音節合成器，逐字元組合注音 |
| `VanguardTrie.TrieGram` | TrieKit | 元圖資料結構（`keyArray` / `value` / `probability` / `previous` / `anterior`）。原為 5 元 tuple，已改具名 struct。**Phase 213 前**的 LibVanguard `LexiconKit` 曾以 `public typealias HomaGram = VanguardTrie.TrieGram` 引用之，該模組已退場；macOS／LibVanguard 兩倉現以 `Homa.Gram` 為組字引擎的元圖型別，另有 `Homa.Gram.init(_ trieGram:)` 橋接。 |
