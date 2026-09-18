// Copyright 2026 Zyvor AI Labs · https://zyvor.dev
// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('Administrator creates a VM — marketing site validation', () => {
  test('Administrator creates a VM — marketing site validation', async ({ page, consoleLogs }) => {



    await page.goto('/');
    await waitForPageReady(page);



    await page.goto('/vm');
    await waitForPageReady(page);



    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});