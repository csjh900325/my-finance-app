exports.handler = async function (event) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
  };
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }
  const codes = (event.queryStringParameters && event.queryStringParameters.codes) || '';
  if (!codes) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Missing codes' }) };
  }
  const codeList = codes.split(',').map(c => c.trim()).filter(Boolean);
  const results = {};

  try {
    // 1) TWSE realtime API - query both TSE and OTC for all codes at once
    const exCh = codeList.map(c => 'tse_' + c + '.tw|otc_' + c + '.tw').join('|');
    const url = 'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=' + exCh + '&_=' + Date.now();
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://mis.twse.com.tw/stock/fibest.jsp',
        'Accept': 'application/json, text/javascript, */*',
      },
    });
    if (res.ok) {
      const raw = await res.text();
      let data;
      try { data = JSON.parse(raw); } catch (e) {
        const m = raw.match(/\{[\s\S]*\}/);
        if (m) data = JSON.parse(m[0]);
      }
      if (data && data.msgArray) {
        data.msgArray.forEach(item => {
          if (!item.c || results[item.c]) return;
          let price = null;
          if (item.z && item.z !== '-') price = parseFloat(item.z);
          if (!price && item.y && item.y !== '-') price = parseFloat(item.y);
          if (!price && item.o && item.o !== '-') price = parseFloat(item.o);
          const prev = (item.y && item.y !== '-') ? parseFloat(item.y) : null;
          if (price && !isNaN(price)) {
            results[item.c] = {
              code: item.c,
              name: item.n ? item.n.trim() : item.c,
              price, prevClose: prev,
              change: prev ? +(price - prev).toFixed(2) : null,
              changePct: prev ? +(((price - prev) / prev) * 100).toFixed(2) : null,
              time: item.t || null,
              volume: item.v || null,
              market: item.ex === 'tse' ? '上市' : '上櫃',
            };
          }
        });
      }
    }

    // 2) Yahoo Finance fallback for missing codes
    const missing = codeList.filter(c => !results[c]);
    for (const code of missing) {
      for (const suffix of ['.TW', '.TWO']) {
        try {
          const yUrl = 'https://query2.finance.yahoo.com/v8/finance/chart/' + code + suffix + '?range=1d&interval=1d';
          const yRes = await fetch(yUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } });
          if (yRes.ok) {
            const yData = await yRes.json();
            const meta = yData && yData.chart && yData.chart.result && yData.chart.result[0] && yData.chart.result[0].meta;
            if (meta && meta.regularMarketPrice) {
              const prev = meta.chartPreviousClose || meta.previousClose || null;
              results[code] = {
                code,
                name: meta.shortName || meta.symbol || code,
                price: meta.regularMarketPrice,
                prevClose: prev,
                change: prev ? +(meta.regularMarketPrice - prev).toFixed(2) : null,
                changePct: prev ? +(((meta.regularMarketPrice - prev) / prev) * 100).toFixed(2) : null,
                time: null, volume: null,
                market: suffix === '.TW' ? '上市' : '上櫃',
              };
              break;
            }
          }
        } catch (e) { /* skip */ }
      }
    }

    if (Object.keys(results).length > 0) {
      return {
        statusCode: 200, headers,
        body: JSON.stringify({
          success: true, data: results,
          found: Object.keys(results).length,
          requested: codeList.length,
          notFound: codeList.filter(c => !results[c]),
          timestamp: new Date().toISOString(),
        }),
      };
    }
    return {
      statusCode: 502, headers,
      body: JSON.stringify({ success: false, error: '無法取得股價，可能是非交易時段或代號有誤', requested: codeList }),
    };
  } catch (err) {
    return {
      statusCode: 500, headers,
      body: JSON.stringify({ success: false, error: err.message }),
    };
  }
};
