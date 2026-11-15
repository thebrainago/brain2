# Chẩn đoán nguồn SEEKER

Lúc 2026-11-07 03:01. Hạn bản chụp: 3 ngày. Không quét 311 URL.

unknown = chưa đo. stale = bản chụp cũ, không phải số 0 mới. no_data chỉ khi bộ đọc chạy đúng và nguồn rỗng. 1065/83 màn hình MQL5 không phải quy tắc dùng được.

- Nguồn trong sổ: **311**
- Quy tắc dùng được (đã giải mã điểm vào và OOS): **0**
- Lần quét sổ gần nhất: 2026-10-20 21:05 — đã xét 2

## Theo loại

- unknown: 166
- not_implemented: 113
- auth: 18
- stale: 14

## Bản lịch sử công khai (không phải ĐẠT của mình)

- Lúc 2026-11-03 05:40: id 1600, đọc 1562, màn hình đạt ngưỡng 1065.

## Smoke có giới hạn

- mql5_tin_hieu_mot: ok — HTTP 200
- exness_mot: network — ConnectionError: HTTPSConnectionPool(host='social-trading.exness.com', port=443): Max retries exceeded with url: /strategy/110170778 (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7f7d47b29eb0>: Failed to resolve 'social-trading.exness.com' ([Errno -2] Name or service not known)"))

## Ngoài sổ 311

- forex_station: stale / bản parse — bản 2026-11-03 (4 ngày) — không phải phép đo hôm nay. không nằm trong 311 dòng sổ. Bản: HTTP 200, chủ đề=0.
- litefinance: stale / bản no_data — bản 2026-11-03 05:40 (4 ngày) — không phải phép đo hôm nay. bản ghi 16 hồ sơ danh sách CHƯA ĐO (thiếu DD/tuổi) và chi tiết không công khai. Không phải 0 trader.
- exness: stale / bản network — bản 2026-11-03 05:40 (4 ngày) — không phải phép đo hôm nay. bản ghi 'loi', không phải challenge và không phải 0 chiến lược. Giả thuyết DNS 198.18.0.1 chưa được bản này chứng minh.

## Nguồn (rút gọn)

| mã | loại | bản | adapter | lần thành công | quy tắc |
|---|---|---|---|---|---|
| allocatesmartly | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| alphaarchitect | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| alvarezquant | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| api_alphavantage | auth | — | — | — | 0 |
| api_binance | auth | — | — | — | 0 |
| api_bybit | auth | — | — | — | 0 |
| api_collective2 | auth | — | — | — | 0 |
| api_darwinex | auth | — | — | — | 0 |
| api_myfxbook | auth | — | — | — | 0 |
| api_oanda | auth | — | — | — | 0 |
| api_okx | auth | — | — | — | 0 |
| api_polygon | auth | — | — | — | 0 |
| api_quantconnect | auth | — | — | — | 0 |
| arabictrader | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| ariva_forum | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| arxiv | stale | robots | nhan.nguon_seeker.quet_mot | — | 0 |
| babypips_forum | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| bankier_forum | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| blog | not_implemented | — | — | — | 0 |
| boursorama_forum | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| buildalpha | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| cnblogs_trung | not_implemented | — | — | — | 0 |
| collective2 | auth | — | — | — | 0 |
| crossref | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| ctrader_algo | auth | — | — | — | 0 |
| ctrader_copy | auth | — | — | — | 0 |
| darwinex | auth | — | — | — | 0 |
| duplitrade | not_implemented | — | — | — | 0 |
| ea_marketplace_ngoai | not_implemented | — | — | — | 0 |
| elitetrader | not_implemented | — | — | — | 0 |
| etoro | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| facebook | auth | — | — | — | 0 |
| fh_financial_hacker | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| followingthetrend | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| forex_nawigator | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| forexfactory | stale | parse | nhan.nguon_seeker.quet_mot | — | 0 |
| forexfactory_ea_threads | stale | parse | nhan.nguon_seeker.quet_mot | — | 0 |
| forexfactory_trade_explorer | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| forexforum_tr | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| futures_io | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fx168 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fxblue | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fxblue_com | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fxblue_market | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fxon | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| fxstat | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gestaltu | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_addyosmani_agent_skills | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_awesome_claude_skills | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_caveman | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_tech_leads_club_agent_skills | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| github | stale | ok | nhan.nguon_seeker.quet_mot | 2026-11-03 | 0 |
| github_mql5 | stale | ok | nhan.nguon_seeker.quet_mot | 2026-11-03 | 0 |
| gogojungle | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| habr_nga | not_implemented | — | — | — | 0 |
| hackernews | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| hangukquant | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| headlandstech | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| indomt5 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| lean_algo | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mmgp | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_articles | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_bai_viet | not_implemented | — | — | — | 0 |
| mql5_code | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_codebase | stale | ok | nhan.nguon_seeker.quet_mot | 2026-11-03 | 0 |
| mql5_forum_ru | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_ma_expert | not_implemented | — | — | — | 0 |
| mql5_market_free | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_signals | stale | ok | ban_chup_chuyen_biet | 2026-11-03 05:40 | 0 |
| mql5_tin_hieu_mt5 | stale | ok | nhan.nguon_seeker.quet_mot | 2026-11-03 05:40 | 0 |
| mrzepczynski | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| myfxbook | stale | challenge | ban_chup_chuyen_biet | — | 0 |
| myfxbook_autotrade | stale | challenge | ban_chup_chuyen_biet | — | 0 |
| nen_alpaca_challenges | not_implemented | — | — | — | 0 |
| nen_alpha_capital_group | not_implemented | — | — | — | 0 |
| nen_apex_trader_funding | not_implemented | — | — | — | 0 |
| nen_barclayhedge_cta_index | not_implemented | — | — | — | 0 |
| nen_binance_okx_bybit_copy_trade | not_implemented | — | — | — | 0 |
| nen_bloomberg_reuters_top_50_hf | not_implemented | — | — | — | 0 |
| nen_collective2_c2 | not_implemented | — | — | — | 0 |
| nen_copyfx_roboforex | not_implemented | — | — | — | 0 |
| nen_darwinex_d_live | not_implemented | — | — | — | 0 |
| nen_e8_funding | not_implemented | — | — | — | 0 |
| nen_earn2trade | not_implemented | — | — | — | 0 |
| nen_etoro_popular_investor | not_implemented | — | — | — | 0 |
| nen_eurekahedge_hfri | not_implemented | — | — | — | 0 |
| nen_ftmo_leaderboard | not_implemented | — | — | — | 0 |
| nen_fundednext | not_implemented | — | — | — | 0 |
| nen_funderpro | not_implemented | — | — | — | 0 |
| nen_fx_blue | not_implemented | — | — | — | 0 |
| nen_hfm_awards | not_implemented | — | — | — | 0 |
| nen_hungarian_trading_championship | not_implemented | — | — | — | 0 |
| nen_kaggle | not_implemented | — | — | — | 0 |
| nen_moneyshow_top_traders | not_implemented | — | — | — | 0 |
| nen_mql5_market | not_implemented | — | — | — | 0 |
| nen_mql5_signals | not_implemented | — | — | — | 0 |
| nen_myfxbook_autotrade | not_implemented | — | — | — | 0 |
| nen_nilssonhedge | not_implemented | — | — | — | 0 |
| nen_numerai_tournament | not_implemented | — | — | — | 0 |
| nen_optiver_jane_street_imc_two_sigma | not_implemented | — | — | — | 0 |
| nen_peak_index | not_implemented | — | — | — | 0 |
| nen_quantconnect_competitions | not_implemented | — | — | — | 0 |
| nen_quantinsti_contests | not_implemented | — | — | — | 0 |
| nen_robbins_world_cup_futures_championship | not_implemented | — | — | — | 0 |
| nen_roboforex_exness_alpari_contests | not_implemented | — | — | — | 0 |
| nen_sg_cta_sg_trend_index | not_implemented | — | — | — | 0 |
| nen_signal_start | not_implemented | — | — | — | 0 |
| nen_stockcharts_contests | not_implemented | — | — | — | 0 |
| nen_swissquote_oanda_comps | not_implemented | — | — | — | 0 |
| nen_the5ers | not_implemented | — | — | — | 0 |
| nen_topstep_trader_combine | not_implemented | — | — | — | 0 |
| nen_toptier_trader | not_implemented | — | — | — | 0 |
| nen_trading_cup_tradingcup_com | not_implemented | — | — | — | 0 |
| nen_tradingview_house_cup_tthc | not_implemented | — | — | — | 0 |
| nen_us_investing_championship_usic | not_implemented | — | — | — | 0 |
| nen_world_cup_of_automated_trading_wccta_ne | not_implemented | — | — | — | 0 |
| nen_worldquant_brain_websim | not_implemented | — | — | — | 0 |
| nen_zulutrade | not_implemented | — | — | — | 0 |
| newtraderu | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| note_fx | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| openalex | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| pantip_sinlapa | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| paperswithcode | not_implemented | — | — | — | 0 |
| priceactionlab | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| qiita_nhat | not_implemented | — | — | — | 0 |
| qoppac | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quant | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantconnect | stale | ok | nhan.nguon_seeker.quet_mot | 2026-10-20 21:05:05 | 0 |
| quantconnect_alpha | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantconnect_forum | not_implemented | — | — | — | 0 |
| quantdare | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantifiedstrategies | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantinsti | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantitativo | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantpedia | not_implemented | — | — | — | 0 |
| quantpedia_blog | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| quantumtrading | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| rankia_foros | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| reddit_algotrading | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| reddit_algotrading_nam | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| reddit_quant | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| reddit_td | not_implemented | — | — | — | 0 |
| robotwealth | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| semantic | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| signalstart | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| smartlab | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| smartlab_blog | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| smartlab_nga | not_implemented | — | — | — | 0 |
| ssrn_quantpedia | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| stackexchange | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_autotraderzrobotchallenges | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_backtestingchartbyeazychan | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_bestexpertadvisors | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_cauvangso1 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_cryptoutu | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_developer_ea_mt5 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_ea | not_implemented | — | — | — | 0 |
| telegram_etherdrops_news | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_forexeatradingchannel | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_forexflarefxrobot | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_forexfreeea | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_jmqg69 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_juanma69 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_mql5decompile | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_pine_script1 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_pinescripter | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_quanttradingvn | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_soltradingbot_channel | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_sp77forex | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_tigeraiquantitative888888 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_trading_bot1 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_trading_bot9 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| telegram_trinvz | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| thaiforexschool | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| thinknewfound | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tiktok | auth | — | — | — | 0 |
| tqtj_ru | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tr8dr | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| traderslaboratory | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| traderviet | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| traderviet_ea | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tradeview_mt4_signals | not_implemented | — | — | — | 0 |
| tradingmarkets | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tradingqna | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tradingview_blog | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tradingview_ideas | not_implemented | — | — | — | 0 |
| tradingview_pine | stale | not_implemented | nhan.nguon_seeker.quet_mot | — | 0 |
| tradingview_scripts | stale | not_implemented | ban_chup_chuyen_biet | — | 0 |
| tradingview_strategies | stale | not_implemented | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_aligrithm | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_betterbuyandhold | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_beyondpassive | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_capitalspectator | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_concretumgroup | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_crackingmarkets | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_factorinvestor | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_fxmacrodata | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_gatambook | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_investresolve | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_jonathankinlay | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_mebfaber | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_morguelabs | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_outcastbeta | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_oxford_capital | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_papertoprofit | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_philosophicaleconomics | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quant_galore | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quantfiction | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quantforhire | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quantifiableedges | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quantish | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_quantjourney | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_returnstacked | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_rulyfi | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_sixfigureinvesting | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_therefutation | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| tutim_todotrader | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| velog_han | not_implemented | — | — | — | 0 |
| wallstreet_online | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| x | auth | — | — | — | 0 |
| youtube | not_implemented | — | — | — | 0 |
| zulutrade | auth | — | — | — | 0 |
| gh_pine_strategies_v6 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_pine_lepotorico | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_tv_dharaarpan | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_backtrader_jasgin | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_nnfx_backtrader | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_bt_multi_asset | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_orb_mt5 | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_gold_pro_scalper | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_mt5_grid_precision | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_gp_fx_strategy | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_fxmacrodata_examples | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_pine_forex | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_backtrader_fx | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_mql5_meanrev | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_mql5_breakout | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_code_mt4_experts | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_code_mt5_indicators | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| mql5_articles_mt5_trading_systems | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| arxiv_fx_trading_strategy | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| arxiv_index_anomaly | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| arxiv_intraday_seasonality | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| openalex_currency_momentum | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| openalex_fx_mean_reversion | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| ssrn_fx_anomaly | not_implemented | — | — | — | 0 |
| tu_facebook_com_forexfactory | not_implemented | — | — | — | 0 |
| tu_faireconomy_com | not_implemented | — | — | — | 0 |
| tu_x_com_forexfactory | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1190104 | not_implemented | — | — | — | 0 |
| tu_twitter_com_forexfactory | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_374228 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1014708 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_655033 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_johnmacknamara_r_factor_portfolio_mean_r | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_midasalgo_midasalgo_11730585 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_479597 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_9049 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_alexander1x_multi_ea_trading_12055163 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_optin_trading_system_always_plus_1178727 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1254177 | not_implemented | — | — | — | 0 |
| tu_paybackfx_com | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_midasalgo | not_implemented | — | — | — | 0 |
| tu_x_com_elitescalpers | not_implemented | — | — | — | 0 |
| tu_x_com_center_forex | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_community_strategies_11_1 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1390964 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_912456 | not_implemented | — | — | — | 0 |
| tu_cryptocraft_com_thread_877901 | not_implemented | — | — | — | 0 |
| tu_x_com_willyalgotrader | not_implemented | — | — | — | 0 |
| tu_signalstart_com | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_592890 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1311538 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_127271 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1428164 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1349515 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1429797 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1331012 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_26044 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1190190 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_236210 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_1308721 | not_implemented | — | — | — | 0 |
| tu_forexfactory_com_thread_669343 | not_implemented | — | — | — | 0 |
| tu_metalsmine_com_thread_922895 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_systems_2 | not_implemented | — | — | — | 0 |
| tu_twitter_com_myfxbook | not_implemented | — | — | — | 0 |
| tu_t_me_myfxbook_official | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_midasalgo_midasalgo_goldenfingers_116060 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_midasalgo_midasalgo_lexo_ultimate_116199 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_fx_challenger_tashron_12245502 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_iminwarn_555_6426348 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_lovethepips_actual_forex_trading_samuel_ | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_ferrari2009_ic_markets_3534905 | not_implemented | — | — | — | 0 |
| tu_myfxbook_com_members_azkgroup_mt4_azk_gold_ai_1026f_11811889 | not_implemented | — | — | — | 0 |
| x_quantifiedstrat | unknown | — | — | — | 0 |
| x_empiricalab | unknown | — | — | — | 0 |
| x_crowcaw | unknown | — | — | — | 0 |
| x_hellonhuga | unknown | — | — | — | 0 |
| x_rb_tradingltd | unknown | — | — | — | 0 |
| x_willyalgotrader | unknown | — | — | — | 0 |
| x_kranky_trades | unknown | — | — | — | 0 |
| x_algojan | unknown | — | — | — | 0 |
| x_priceactionlab | unknown | — | — | — | 0 |
| gh_topic_expert_advisor | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_topic_mt5_ea | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_mql4_ea_backtest | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_mql5_ea_backtest | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_gold_ea | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_search_pine_backtest_fx | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| gh_earnforex_repos | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
| earnforex_ea | unknown | — | nhan.nguon_seeker.quet_mot | — | 0 |
