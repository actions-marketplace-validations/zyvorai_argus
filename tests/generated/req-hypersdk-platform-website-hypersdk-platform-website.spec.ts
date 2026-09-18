// Copyright 2026 Zyvor AI Labs · https://zyvor.dev
// SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial

import { test, expect } from '../../playwright/fixtures/base';
import { waitForPageReady } from '../../playwright/utils/helpers';


test.describe('HyperSDK Platform Website', () => {
  test('HyperSDK Platform Website', async ({ page, consoleLogs }) => {



    await page.goto('/');
    await waitForPageReady(page);



    const appErrors = consoleLogs.filter(
      (l) => l.startsWith('[error]') && !l.includes('Content Security Policy')
    );
    expect(appErrors).toHaveLength(0);
  });
});