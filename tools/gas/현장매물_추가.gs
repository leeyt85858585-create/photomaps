// ===== 현장 매물 추가 (2026.10.23) =====
// 1) doPost 안의 "if (p.action === 'listpos') ..." 줄 바로 아래에 이 두 줄을 넣으세요.
//      if (p.action === 'listadd') return out_(listadd_(p));
//      if (p.action === 'fieldlist') return out_(fieldlist_());
// 2) 아래 함수들을 스크립트 맨 아래에 붙여넣으세요.
// 3) 배포 > 배포 관리 > 연필(수정) > 버전: 새 버전 > 배포  (웹앱 주소는 그대로 유지됨)
//
// 지도에서 등록한 매물은 이 스프레드시트(임장기록)의 '현장매물' 탭에 쌓입니다.
// '임장 매물DB' 원본 시트는 건드리지 않습니다.
const FLHEAD = ['id', '매물명', '주소', '상권', '월세', '보증금', '권리금', '특이사항', '위도', '경도', '확인일', '입력자', '등록시각'];
function fieldSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let s = ss.getSheetByName('현장매물');
  if (!s) { s = ss.insertSheet('현장매물'); s.appendRow(FLHEAD); s.setFrozenRows(1); s.getRange('A:A').setNumberFormat('@'); }
  return s;
}
function listadd_(p) {
  const s = fieldSheet_(), n = s.getLastRow();
  if (n >= 2) { const ids = s.getRange(2, 1, n - 1, 1).getValues(); for (let i = 0; i < ids.length; i++) if (String(ids[i][0]) === String(p.id)) return { ok: true, dup: true }; }
  const now = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
  s.appendRow([String(p.id), p.name || '', p.addr || '', p.area || '', p.rent, p.dep, p.key, p.note || '', p.lat, p.lng, p.date || '', p.who || '', now]);
  return { ok: true };
}
function fieldlist_() {
  const s = fieldSheet_(), v = s.getDataRange().getValues();
  if (v.length < 2) return { ok: true, rows: [] };
  const head = v[0];
  return { ok: true, rows: v.slice(1).map(r => { const o = {}; head.forEach((h, i) => { o[h] = r[i]; }); return o; }) };
}
