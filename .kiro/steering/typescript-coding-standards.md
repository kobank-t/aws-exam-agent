---
inclusion: fileMatch
fileMatchPattern: "*.ts"
---

# TypeScript コーディング規約 (E2E テスト用)

## 概要

AWS Exam Coach プロジェクトにおける TypeScript コーディング規約です。Playwright E2E テスト専用として、学習重視のシンプルな規約を定義します。

**Playwright MCP Server 統合**: プロジェクトでは `@playwright/mcp` を通じて Playwright 機能を MCP（Model Context Protocol）経由で利用可能です。これにより、AI エージェントがブラウザ自動化を直接実行できます。

## 基本方針

### 1. 学習重視の軽量規約

- E2E テスト（Playwright）でのみ TypeScript を使用
- 複雑な TypeScript 機能は避け、基本に集中
- Playwright 公式ベストプラクティスに準拠

### 2. 一貫性の確保

- E2E テスト内で統一された TypeScript スタイルを維持
- プロジェクト全体の品質基準・命名規則の統一感を保持
- 開発チーム内での認知負荷を軽減

## プロジェクト構成

### テストディレクトリ構造

```
tests/
├── e2e/
│   ├── fixtures/           # カスタムフィクスチャ
│   ├── pages/             # Page Object Model
│   ├── specs/             # テストファイル (*.spec.ts)
│   └── utils/             # テストユーティリティ
├── tsconfig.json          # TypeScript設定
├── playwright.config.ts   # Playwright設定
└── .eslintrc.json        # ESLint設定
```

## TypeScript 設定

### tsconfig.json (推奨設定)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@fixtures/*": ["fixtures/*"],
      "@pages/*": ["pages/*"],
      "@utils/*": ["utils/*"]
    }
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "test-results"]
}
```

### playwright.config.ts

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./specs",
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
```

## コードスタイル・パターン

### 基本的なテスト構造

```typescript
import { test, expect } from "@playwright/test";

test.describe("問題生成機能", () => {
  test("問題生成から配信までの基本フロー", async ({ page, request }) => {
    // Arrange: テストデータ準備
    const questionData = {
      service: "EC2",
      topic: "VPC",
      difficulty: "intermediate",
    };

    // Act: API呼び出し
    const response = await request.post("/api/generate", {
      data: questionData,
    });

    // Assert: レスポンス確認
    expect(response.status()).toBe(202);
    const responseBody = await response.json();
    expect(responseBody).toHaveProperty("job_id");

    // Act: Teams UI確認
    await page.goto("https://teams.microsoft.com/...");

    // Assert: UI要素確認
    await expect(
      page.locator('[data-testid="question-message"]')
    ).toBeVisible();
    await expect(page.locator('[data-testid="question-text"]')).toContainText(
      "VPC"
    );
  });
});
```

### Page Object Model パターン

```typescript
import type { Page, Locator } from "@playwright/test";

export class TeamsPage {
  private readonly page: Page;
  private readonly questionMessage: Locator;
  private readonly reactionButtons: Locator;
  private readonly answerReveal: Locator;

  constructor(page: Page) {
    this.page = page;
    this.questionMessage = page.locator('[data-testid="question-message"]');
    this.reactionButtons = page.locator('[data-testid="reaction-button"]');
    this.answerReveal = page.locator('[data-testid="answer-reveal"]');
  }

  async navigateToChannel(channelUrl: string): Promise<void> {
    await this.page.goto(channelUrl);
    await this.page.waitForLoadState("networkidle");
  }

  async waitForQuestionToAppear(): Promise<void> {
    await this.questionMessage.waitFor({ state: "visible" });
  }

  async selectAnswer(option: "A" | "B" | "C" | "D"): Promise<void> {
    await this.reactionButtons.filter({ hasText: option }).click();
  }

  async waitForAnswerReveal(): Promise<string> {
    await this.answerReveal.waitFor({ state: "visible" });
    return (await this.answerReveal.textContent()) || "";
  }
}
```

### カスタムフィクスチャ

```typescript
import { test as base } from "@playwright/test";
import { TeamsPage } from "@pages/TeamsPage";
import { ApiClient } from "@utils/ApiClient";

type TestFixtures = {
  teamsPage: TeamsPage;
  apiClient: ApiClient;
};

export const test = base.extend<TestFixtures>({
  teamsPage: async ({ page }, use) => {
    const teamsPage = new TeamsPage(page);
    await use(teamsPage);
  },

  apiClient: async ({ request }, use) => {
    const apiClient = new ApiClient(request);
    await use(apiClient);
  },
});

export { expect } from "@playwright/test";
```

## ESLint 設定

### .eslintrc.json

```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "plugin:playwright/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module"
  },
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "playwright/expect-expect": "error",
    "playwright/no-conditional-in-test": "error",
    "playwright/no-wait-for-timeout": "warn"
  },
  "env": {
    "node": true,
    "es2022": true
  }
}
```

## 命名規則

### ファイル・ディレクトリ

- **テストファイル**: `*.spec.ts` (例: `question-generation.spec.ts`)
- **Page Object**: `PascalCase.ts` (例: `TeamsPage.ts`)
- **ユーティリティ**: `PascalCase.ts` (例: `ApiClient.ts`)
- **フィクスチャ**: `camelCase.ts` (例: `customFixtures.ts`)

### コード内命名

- **変数・関数**: `camelCase`
- **クラス**: `PascalCase`
- **定数**: `UPPER_SNAKE_CASE`
- **型・インターフェース**: `PascalCase`

### テスト名

```typescript
// ✅ 良い例: 日本語で具体的に記述
test("EC2サービスのVPCトピックで問題生成が成功する", async ({ page }) => {
  // テスト実装
});

test("不正なサービス名でAPI呼び出しが400エラーを返す", async ({ request }) => {
  // テスト実装
});

// ❌ 悪い例: 抽象的・英語のみ
test("should work", async ({ page }) => {
  // テスト実装
});
```

## ベストプラクティス

### 1. 型安全性の確保

```typescript
// ✅ 良い例: 明示的な型定義
interface QuestionRequest {
  service: string;
  topic: string;
  difficulty: "beginner" | "intermediate" | "advanced";
}

const questionData: QuestionRequest = {
  service: "EC2",
  topic: "VPC",
  difficulty: "intermediate",
};

// ❌ 悪い例: any型の使用
const questionData: any = {
  service: "EC2",
  topic: "VPC",
  difficulty: "intermediate",
};
```

### 2. 非同期処理の適切な待機

```typescript
// ✅ 良い例: Playwrightの待機機能を活用
await expect(page.locator('[data-testid="question"]')).toBeVisible();
await page.waitForLoadState("networkidle");

// ❌ 悪い例: 固定時間の待機
await page.waitForTimeout(5000);
```

### 3. エラーハンドリング

```typescript
// ✅ 良い例: 適切なエラーハンドリング
test("API エラー時の適切な処理", async ({ request }) => {
  const response = await request.post("/api/generate", {
    data: { service: "InvalidService" },
  });

  expect(response.status()).toBe(400);
  const errorBody = await response.json();
  expect(errorBody).toHaveProperty("error");
  expect(errorBody.error).toContain("無効なサービス名");
});
```

## MCP Server 統合

### Playwright MCP Server の活用

プロジェクトでは `@playwright/mcp@latest` を通じて、AI エージェントが Playwright 機能を直接利用できます：

```typescript
// MCP Server経由でのブラウザ操作例
// AI エージェントが以下のような操作を自動実行可能

// 1. ページナビゲーション
await page.goto("https://teams.microsoft.com/channel/...");

// 2. 要素操作
await page.click('[data-testid="reaction-button-A"]');
await page.fill('[data-testid="message-input"]', "テストメッセージ");

// 3. アサーション
await expect(page.locator('[data-testid="question-text"]')).toBeVisible();
```

### MCP 統合の利点

- **AI エージェント連携**: 手動テスト実行から AI 主導のテスト自動化へ
- **リアルタイム検証**: 開発中の機能を AI が即座にテスト実行
- **学習効率向上**: AI がテストパターンを学習・提案

## 学習効果

この TypeScript 規約により、以下の技術を実践的に学習できます：

- **TypeScript 基礎**: 型安全性、インターフェース、ジェネリクス
- **Playwright API**: ブラウザ自動化、API テスト、フィクスチャ
- **MCP 統合**: Model Context Protocol を通じた AI 連携
- **テスト設計**: Page Object Model、テストの構造化
- **非同期プログラミング**: Promise、async/await パターン
- **モダン JavaScript**: ES2022 機能、モジュールシステム

## 開発ツール設定

### VS Code 設定 (.vscode/settings.json)

```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll.eslint": true
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Prettier 設定 (.prettierrc)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

---

**適用範囲**: AWS Exam Coach プロジェクト E2E テスト  
**更新日**: 2025 年 8 月 1 日  
**バージョン**: 1.0
