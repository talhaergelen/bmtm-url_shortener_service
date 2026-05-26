/**
 * load-test.js — k6 Performans Test Senaryosu
 *
 * Bu dosya ne işe yarar?
 *   URL Shortener API'sini yüksek yük altında test eder.
 *   p95 latency (en yavaş %5 dışında kalan isteklerin süresi) ölçer.
 *
 * k6 nedir?
 *   Modern performans test aracı. JavaScript ile yazılır.
 *   Sanal kullanıcılar oluşturur, istekler gönderir, sonuçları ölçer.
 *
 * Kılavuz gereksinimi:
 *   "k6 ile 1 senaryo + p95 latency ölçümü"
 *
 * Kurulum:
 *   https://k6.io/docs/get-started/installation/
 *   Windows: choco install k6
 *   macOS: brew install k6
 *
 * Çalıştırma:
 *   k6 run perf/load-test.js
 *   k6 run perf/load-test.js --out json=perf/results.json
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// ─────────────────────────────────────────────────────────
// ÖZEL METRİKLER
// ─────────────────────────────────────────────────────────

// Başarı oranı — kaç istek başarılı?
const errorRate = new Rate("error_rate");

// Redirect süresi — yönlendirme ne kadar sürüyor?
const redirectDuration = new Trend("redirect_duration");

// ─────────────────────────────────────────────────────────
// TEST AYARLARI
// ─────────────────────────────────────────────────────────

export const options = {
  // Aşamalar (stages) — yük kademeli artıp azalır
  stages: [
    { duration: "30s", target: 10 },   // 0→10 kullanıcıya kademeli çıkış
    { duration: "1m",  target: 50 },   // 50 kullanıcıda 1 dakika sabit yük
    { duration: "30s", target: 100 },  // 100 kullanıcıya çıkış (pik test)
    { duration: "30s", target: 0 },    // Kademeli iniş
  ],

  // Başarı Kriterleri (thresholds)
  // Bu kriterler karşılanmazsa test "başarısız" sayılır
  thresholds: {
    // p95 latency < 500ms (500 milisaniye)
    "http_req_duration": ["p(95)<500"],

    // Hata oranı < %5
    "error_rate": ["rate<0.05"],

    // Redirect süresi p95 < 200ms
    "redirect_duration": ["p(95)<200"],
  },
};

// API adresi
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

// ─────────────────────────────────────────────────────────
// SETUP — Test başlamadan önce çalışır
// ─────────────────────────────────────────────────────────

export function setup() {
  console.log(`\n🚀 Performans testi başlıyor: ${BASE_URL}`);

  // Test için birkaç URL oluştur
  const urls = [];
  const testUrls = [
    "https://www.google.com",
    "https://github.com",
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://stackoverflow.com",
  ];

  for (const originalUrl of testUrls) {
    const res = http.post(
      `${BASE_URL}/shorten`,
      JSON.stringify({ original_url: originalUrl }),
      { headers: { "Content-Type": "application/json" } }
    );

    if (res.status === 201) {
      const data = JSON.parse(res.body);
      urls.push(data.short_code);
    }
  }

  console.log(`✅ ${urls.length} test URL'si oluşturuldu: ${urls.join(", ")}`);
  return { shortCodes: urls };
}

// ─────────────────────────────────────────────────────────
// ANA TEST FONKSİYONU — Her sanal kullanıcı bunu çalıştırır
// ─────────────────────────────────────────────────────────

export default function (data) {
  const shortCodes = data.shortCodes;

  // Rastgele bir senaryo seç
  const scenario = Math.random();

  if (scenario < 0.4) {
    // SENARYO A: URL Kısaltma (%40 olasılık)
    scenarioShorten();
  } else if (scenario < 0.7) {
    // SENARYO B: Redirect (%30 olasılık)
    if (shortCodes.length > 0) {
      const code = shortCodes[Math.floor(Math.random() * shortCodes.length)];
      scenarioRedirect(code);
    }
  } else if (scenario < 0.9) {
    // SENARYO C: İstatistik görüntüleme (%20 olasılık)
    if (shortCodes.length > 0) {
      const code = shortCodes[Math.floor(Math.random() * shortCodes.length)];
      scenarioStats(code);
    }
  } else {
    // SENARYO D: Listeleme (%10 olasılık)
    scenarioList();
  }

  // İstekler arasında kısa bekle (gerçek kullanıcı davranışını simüle et)
  sleep(Math.random() * 0.5 + 0.1); // 0.1-0.6 saniye
}

// ─────────────────────────────────────────────────────────
// SENARYOLAR
// ─────────────────────────────────────────────────────────

function scenarioShorten() {
  const payload = JSON.stringify({
    original_url: `https://example.com/test-${Math.floor(Math.random() * 10000)}`,
  });

  const res = http.post(`${BASE_URL}/shorten`, payload, {
    headers: { "Content-Type": "application/json" },
    tags: { scenario: "shorten" },
  });

  const success = check(res, {
    "shorten: status 201": (r) => r.status === 201,
    "shorten: short_code exists": (r) => {
      try {
        return JSON.parse(r.body).short_code !== undefined;
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!success);
}

function scenarioRedirect(shortCode) {
  const start = Date.now();

  const res = http.get(`${BASE_URL}/${shortCode}`, {
    redirects: 0, // Redirect'i takip etme, sadece ölç
    tags: { scenario: "redirect" },
  });

  const duration = Date.now() - start;
  redirectDuration.add(duration);

  const success = check(res, {
    "redirect: status 301": (r) => r.status === 301,
    "redirect: location header exists": (r) => r.headers["Location"] !== undefined,
  });

  errorRate.add(!success);
}

function scenarioStats(shortCode) {
  const res = http.get(`${BASE_URL}/stats/${shortCode}`, {
    tags: { scenario: "stats" },
  });

  const success = check(res, {
    "stats: status 200": (r) => r.status === 200,
    "stats: click_count field": (r) => {
      try {
        return JSON.parse(r.body).click_count !== undefined;
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!success);
}

function scenarioList() {
  const res = http.get(`${BASE_URL}/urls/list?limit=10`, {
    tags: { scenario: "list" },
  });

  const success = check(res, {
    "list: status 200": (r) => r.status === 200,
    "list: is array": (r) => {
      try {
        return Array.isArray(JSON.parse(r.body));
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!success);
}

// ─────────────────────────────────────────────────────────
// TEARDOWN — Test bittikten sonra çalışır
// ─────────────────────────────────────────────────────────

export function teardown(data) {
  console.log("\n✅ Performans testi tamamlandı!");
  console.log("📊 Sonuçları görmek için: k6 run perf/load-test.js --out json=perf/results.json");
}
