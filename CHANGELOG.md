# Changelog

## [0.2.0](https://github.com/chrisimcevoy/purepyodbc/compare/v0.1.0...v0.2.0) (2025-06-03)


### Features

* initial mysql support ([#39](https://github.com/chrisimcevoy/purepyodbc/issues/39)) ([5155704](https://github.com/chrisimcevoy/purepyodbc/commit/5155704406c5ee1e85ea9f4bb3c8854d40e8aa61))


### Bug Fixes

* guard against double SQLDisconnect ([#53](https://github.com/chrisimcevoy/purepyodbc/issues/53)) ([da25126](https://github.com/chrisimcevoy/purepyodbc/commit/da2512682507e0b2258412d5866fa227598c96ef))
* heap corruption in SQLGetData call ([#49](https://github.com/chrisimcevoy/purepyodbc/issues/49)) ([267d2f2](https://github.com/chrisimcevoy/purepyodbc/commit/267d2f2ac221d625038ed631a03fbca796349bf2))
* Verify `cursor.foreignKeys` with MySQL ([#51](https://github.com/chrisimcevoy/purepyodbc/issues/51)) ([41c50ac](https://github.com/chrisimcevoy/purepyodbc/commit/41c50ac78a3b227d50f9236a3f4ba565fbbcb529))

## 0.1.0 (2024-10-27)


### Features

* autocommit ([#18](https://github.com/chrisimcevoy/purepyodbc/issues/18)) ([db638bd](https://github.com/chrisimcevoy/purepyodbc/commit/db638bdc09bd49fca84f8f3d333717d1556501fb))


### Bug Fixes

* ci badge in readme.md ([#22](https://github.com/chrisimcevoy/purepyodbc/issues/22)) ([658d4ca](https://github.com/chrisimcevoy/purepyodbc/commit/658d4ca84b06ad331b8c9182d745cc432dff4524))
* consolidate package version ([#24](https://github.com/chrisimcevoy/purepyodbc/issues/24)) ([badedff](https://github.com/chrisimcevoy/purepyodbc/commit/badedff1b51937690af66e780780cd9857093b19))
* explicitly state version attributes ([#29](https://github.com/chrisimcevoy/purepyodbc/issues/29)) ([d97ffe4](https://github.com/chrisimcevoy/purepyodbc/commit/d97ffe4fe1c08187b0b743be94cf1fafe49f50e5))
* move version to top of module ([#26](https://github.com/chrisimcevoy/purepyodbc/issues/26)) ([250a279](https://github.com/chrisimcevoy/purepyodbc/commit/250a279919f2e54d5fa548459e90abea99adc33f))
* remove dunder version ([#27](https://github.com/chrisimcevoy/purepyodbc/issues/27)) ([96399e7](https://github.com/chrisimcevoy/purepyodbc/commit/96399e725c48cc58c25c9de50ce50dc4867aa3c1))
* remove spurious comments ([#31](https://github.com/chrisimcevoy/purepyodbc/issues/31)) ([4d11f2f](https://github.com/chrisimcevoy/purepyodbc/commit/4d11f2ffb18846e1d0e898b3c4b9f1a7fa1cf18b))
* try just dunder version ([#28](https://github.com/chrisimcevoy/purepyodbc/issues/28)) ([50478bc](https://github.com/chrisimcevoy/purepyodbc/commit/50478bc072660f1ba56c55f793418cd782ab0375))
* update the version already, please ([#32](https://github.com/chrisimcevoy/purepyodbc/issues/32)) ([64ac3b5](https://github.com/chrisimcevoy/purepyodbc/commit/64ac3b5f338209b5c04c193a45fecf2ed1722338))
* use release-please-manifest.json to specify version files ([#30](https://github.com/chrisimcevoy/purepyodbc/issues/30)) ([cab809d](https://github.com/chrisimcevoy/purepyodbc/commit/cab809d9728da5d0461d734161ac5884f967334a))
* use version string for `version` ([#25](https://github.com/chrisimcevoy/purepyodbc/issues/25)) ([86820f1](https://github.com/chrisimcevoy/purepyodbc/commit/86820f12659b9c405aafcaa048c01efa5e3b7e6c))
* windows `drivers` command on pypy &gt;= v7.3.10 ([#7](https://github.com/chrisimcevoy/purepyodbc/issues/7)) ([7dc5fc8](https://github.com/chrisimcevoy/purepyodbc/commit/7dc5fc8e65cc7bdfc63c3d827022e8c22a077a14))
