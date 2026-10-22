# 도로 유동인구(추정) 재생성 도구

권역 추가 시 생활인구는 다시 받을 필요 없음(slot4.npy에 가공본 보관). 도로·상가만 새로 받으면 됨.

1. bboxes.json에 권역 추가: "id": [남위도, 서경도, 북위도, 동경도]
2. 서울 OSM 받기: https://download.bbbike.org/osm/bbbike/Seoul/Seoul.osm.gz (약 110MB)
3. python3 extract.py Seoul.osm.gz <작업폴더>   → <id>_hw.json, <id>_poi.json
4. python3 flow3.py <id> <작업폴더>/<id>_hw.json <작업폴더>/<id>_poi.json   → 저장소 루트에 flow_<id>.json
5. index.html의 FREG에 {g,n,bb,v} 추가

- slot4.npy: 250m 격자 × 5시간대(주말13~18, 주말18~22, 금토22~24, 평일18~22, 평일15~18) × [내국인 전체, 내국인 10~39세 여성, 단기 외국인, 장기 외국인] 평균 인구. 서울 생활인구(250m) 2026.10.07~10.18 중 10일.
- slot4_ids.json: 격자 ID 순서. agg2.py: 원본 CSV → slot4.npy.
- 색 구간은 flow_hongdae.json의 br을 공통 기준으로 씀.
