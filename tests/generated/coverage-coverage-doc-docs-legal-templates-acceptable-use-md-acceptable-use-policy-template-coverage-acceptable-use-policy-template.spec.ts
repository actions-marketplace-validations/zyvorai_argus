// Copyright 2026 Zyvor AI Labs · https://zyvor.dev
// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Coverage: Acceptable Use Policy (template)', () => {
  test('Coverage: Acceptable Use Policy (template)', async ({ page, consoleLogs }) => {



    await page.goto('/acceptable-use-policy-template');
    await waitForPageReady(page);



    await waitForPageReady(page);




    await expect(page.getByText(/Acceptable Use Policy (template)/i).first()).toBeVisible({ timeout: 15000 });




    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});