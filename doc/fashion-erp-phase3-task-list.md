# Fashion ERP 第三阶段任务清单

本文档用于承接新的业务主线：

`原辅料采购与备货 -> 打样与工艺单 -> 外包下单 -> 商品入库 -> 仓储履约与履约成本 -> 售后闭环 -> 运营/财务报表`

相关文档：

- 产品需求分析：[fashion-erp-product-analysis.md](E:\Dropbox\Syn\Project\frappe_docker_ra\docs\fashion-erp-product-analysis.md)
- 第三阶段实施版：[fashion-erp-phase3-implementation.md](E:\Dropbox\Syn\Project\frappe_docker_ra\docs\fashion-erp-phase3-implementation.md)

## 阶段结论

- 平台 API 同步永久搁置，当前只能手工同步
- ERP 从 `Style` 录入开始承接
- 面料、辅料、包装耗材由我方提供并单独管理
- 打样、工艺单、外包下单是当前主链
- 外包订单只与原料做引用关联，不自动扣减原料库存
- 履约成本包含包装耗材和手工快递费
- 内部生产深化后置

## 任务列表

### T400 第三阶段范围冻结

| 项目 | 内容 |
|---|---|
| 任务编号 | `T400` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 冻结第三阶段范围和最新业务前提 |
| 交付物 | 第三阶段实施文档、产品分析文档 |

### T405 原辅料与耗材主数据

| 项目 | 内容 |
|---|---|
| 任务编号 | `T405` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 建立面料、辅料、包装耗材的分类和属性 |
| 交付物 | `Item / Supplier` 扩展字段、分类规则、Desk 入口 |

### T406 原辅料与耗材采购、入库、备货

| 项目 | 内容 |
|---|---|
| 任务编号 | `T406` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让原辅料和包装耗材可以采购、收货、入库、备货 |
| 交付物 | 标准采购单据扩展、到货与库存规则、采购/收货默认值联动、服务端校验 |

### T410 打样单

| 项目 | 内容 |
|---|---|
| 任务编号 | `T410` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让款式录入后可以发起打样，并跟踪样品状态 |
| 交付物 | 打样单对象、样品状态、基础动作、`Style` 发起入口 |

### T411 工艺单

| 项目 | 内容 |
|---|---|
| 任务编号 | `T411` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 建立工艺单，作为外包下单依据 |
| 交付物 | 工艺单对象、款式关联、版本控制基础 |

### T412 外包下单与预计成本

| 项目 | 内容 |
|---|---|
| 任务编号 | `T412` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 向外包工厂下单，并记录预计成本 |
| 交付物 | 外包单对象、状态流转、工艺单引用、预计成本字段 |

建议范围：

- 外包工厂
- 工艺单引用
- 预计成本
- 预计交期

### T413 外包订单与原辅料关联

| 项目 | 内容 |
|---|---|
| 任务编号 | `T413` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让外包订单能引用所需原辅料，但不自动生成出库 |
| 交付物 | 订单原料子表、人工登记字段、占用视图 |

当前实现说明：

- 已在 `Outsource Order` 上新增 `materials` 子表
- 已具备 `planned_qty / prepared_qty / issued_qty_manual / warehouse / default_location`
- 已接入物料类型、仓库/库位归属和数量上限校验
- 已补外包单级供料视图入口，可直接查看原辅料占用和供料口径

### T414 外包单驱动供料需求与待采购视图

| 项目 | 内容 |
|---|---|
| 任务编号 | `T414` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 基于 `Outsource Order.materials` 建立净需求与待采购口径 |
| 交付物 | `required_qty / on_hand_qty / on_order_qty / prepared_qty / to_purchase_qty` 计算逻辑与视图 |

说明：

- 本任务是对建议中“BOM/供料计划”的改写版
- 当前驱动对象是 `Outsource Order`，不是 `Production Ticket`
- 第一阶段不新建完整 `Supply Plan`，先做外包单驱动的轻量供料视图

当前实现说明：

- 已在服务端按外包单物料聚合生成 `required_qty / on_hand_qty / on_order_qty / prepared_qty / to_purchase_qty`
- 已在 `Outsource Order` 表单补“查看供料视图”入口
- 当前供料视图已形成轻量闭环，采购/收货的精确联动已由 `T415` 补齐

### T415 外包供料联动强化

| 项目 | 内容 |
|---|---|
| 任务编号 | `T415` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 让采购、收货与外包备货视图形成服务端联动 |
| 交付物 | `supply_context=外包备货` 下的回写逻辑、聚合口径、备货跟踪增强 |

说明：

- 这是对建议中“采购执行追踪 / 自动化联动”的改写版
- 关键联动放服务端或 hook，不只依赖 Client Script
- 当前不包含工厂虚拟仓和自动发料库存联动

当前实现说明：

- 已在 `Purchase Order Item / Purchase Receipt Item` 增加 `reference_outsource_order`
- `Purchase Receipt` 可从来源采购行自动回填 `reference_style / reference_outsource_order / reference_sample_ticket / supply_context`
- `supply_context=外包备货` 时，服务端强制校验外包单、款号、打样单、供料清单一致性
- 外包供料视图的 `on_order_qty` 已优先按 `reference_outsource_order` 精确聚合，旧的 `reference_style` 口径只作为兼容回退

### T420 外包到货入库

| 项目 | 内容 |
|---|---|
| 任务编号 | `T420` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 建立第三方外包到货后的收货入库流程 |
| 交付物 | 到货登记、收货入库方案 |

当前实现说明：

- 已新增 `Outsource Receipt`、`Outsource Receipt Item`、`Outsource Receipt Log`
- 已支持收货确认、生成待质检 `Stock Entry` 草稿、确认已入库
- 已按有效到货单累计回写 `Outsource Order.received_qty`

### T421 到货质检与库存状态落账

| 项目 | 内容 |
|---|---|
| 任务编号 | `T421` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让商品入库前先质检，再落入最终库存状态 |
| 交付物 | `QC_PENDING -> SELLABLE / DEFECTIVE / REPAIR / FROZEN` 业务动作 |

当前实现说明：

- 已在到货明细补充可售 / 返修 / 次品 / 冻结数量与质检说明
- 已支持从 `Outsource Receipt` 生成 `QC_PENDING -> SELLABLE / REPAIR / DEFECTIVE / FROZEN` 的质检落账草稿
- 已支持填写 `final_stock_entry` 并执行“确认质检完成”，单据状态可推进到 `已质检`
- 已将 `已质检` 到货单纳入累计到货回写口径

### T422 外包异常处理

| 项目 | 内容 |
|---|---|
| 任务编号 | `T422` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 记录短装、错色、错码、次品等外包异常 |
| 交付物 | 异常字段或异常单据方案 |

当前实现说明：

- 已在 `Outsource Receipt Item` 增加 `shortage_qty / wrong_color_qty / wrong_size_qty / exception_note`，并在 `Outsource Receipt` 头部增加异常行数、短装/错色/错码/次品汇总与异常摘要
- 已允许“零到货 + 短装数量”的纯异常行留痕，这类行不会进入待检入库或质检落账 `Stock Entry`
- 当前方案仍是轻量异常留痕，不包含独立异常单、对厂索赔、责任判定和赔付流程

### T430 手工订单同步策略

| 项目 | 内容 |
|---|---|
| 任务编号 | `T430` |
| 优先级 | `P0` |
| 状态 | `DOING` |
| 目标 | 明确平台订单进入系统的手工同步方式 |
| 交付物 | 导入模板、字段映射、去重规则 |

当前基础：

- `Channel Store` 已可作为渠道/店铺主数据
- `Sales Order` 已具备 `channel / channel_store / external_order_id / biz_type`
- 当前仍缺导入模板、去重规则和批次留痕对象

当前冻结方案：

- 详细方案见 [fashion-erp-order-sync-design.md](E:\Dropbox\Syn\Project\frappe_docker_ra\docs\fashion-erp-order-sync-design.md)
- 标准 CSV 模板见 [fashion-erp-order-sync-template.csv](E:\Dropbox\Syn\Project\frappe_docker_ra\docs\fashion-erp-order-sync-template.csv)
- 第一版输入口径冻结为“订单明细行导入”，按 `channel_store + external_order_id` 聚合为一张 `Sales Order`
- 第一版导入必须提供内部 `item_code`，`platform_sku` 仅留痕，不承担自动映射
- 第一版建议先补 `Channel Store.default_company / default_customer`，避免每次导入重复手填上下文

### T431 手工同步批次

| 项目 | 内容 |
|---|---|
| 任务编号 | `T431` |
| 优先级 | `P0` |
| 状态 | `DOING` |
| 目标 | 记录每次手工导入的批次和结果 |
| 交付物 | 导入批次对象或导入日志方案 |

建议对象：

- `Order Sync Batch`
- `Order Sync Batch Item`

建议分两步落地：

1. 先做批次对象、行对象、默认值与统计字段
2. 再做批次校验、重复预判和正式导入动作

当前实现说明：

- 已新增 `Order Sync Batch`、`Order Sync Batch Item`
- 已给 `Channel Store` 增加 `default_company / default_customer`
- 已新增 `order_sync_service.py`，批次保存时可回填店铺默认值、规范化行数据、计算统计字段，并把行状态推进到 `待导入 / 校验失败`
- 已具备 `preview_import / execute_import`，可预判重复订单、按订单聚合、创建 `Sales Order` 草稿，并回写 `sales_order / sales_order_item_ref`
- 已给 `Sales Order.validate` 增加 `channel_store + external_order_id` 服务端重复校验，并在填写 `channel_store` 时自动同步 `channel`
- 已补 `Sales Order(channel_store, external_order_id)` 数据库索引 patch，待执行 migrate 后正式落库
- 已支持在 `Order Sync Batch` 表单粘贴 CSV 内容导入，支持覆盖/追加两种模式，并记录 `source_hash`
- 当前仍未补附件上传式导入和更完整的导入结果报表

### T432 销售订单履约状态

| 项目 | 内容 |
|---|---|
| 任务编号 | `T432` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 给 `Sales Order / Sales Order Item` 建立履约状态 |
| 交付物 | 订单头状态、订单行状态、推进规则 |

### T433 仓储履约动作

| 项目 | 内容 |
|---|---|
| 任务编号 | `T433` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让仓库能从订单驱动配货、拣货、打包、发货 |
| 交付物 | 履约动作入口与状态推进 |

### T434 包装耗材挂单与出库

| 项目 | 内容 |
|---|---|
| 任务编号 | `T434` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让包装耗材可以挂到出货单并形成出库 |
| 交付物 | 出货单耗材子表、耗材出库逻辑、成本汇总字段 |

### T435 快递费与履约成本

| 项目 | 内容 |
|---|---|
| 任务编号 | `T435` |
| 优先级 | `P0` |
| 状态 | `DONE` |
| 目标 | 让快递费手工录入，并与包装耗材一起形成履约成本 |
| 交付物 | 快递费字段、履约成本汇总逻辑、基础报表口径 |

当前实现说明：

- 已给 `Delivery Note` 增加 `manual_logistics_fee / fulfillment_total_cost` 字段，保存时会把包装耗材估算金额与手工快递费汇总成统一履约总成本
- 已新增履约成本汇总接口，可按日期范围、公司统计已提交 `Delivery Note` 的耗材金额、手工快递费和履约总成本
- 当前金额口径仍为“包装耗材估算金额 + 手工快递费”，暂未纳入真实快递账单和更细的仓内人工成本

### T440 售后与订单闭环

| 项目 | 内容 |
|---|---|
| 任务编号 | `T440` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 让售后工单状态影响订单闭环 |
| 交付物 | 售后与订单状态回写规则 |

当前实现说明：

- 已可从售后工单生成补发销售订单草稿
- `Sales Order.after_sales_ticket` 保存后会回写 `After Sales Ticket.replacement_sales_order`
- 售后工单激活时会把原销售订单头状态推进为 `售后中`，命中的销售订单行推进为 `售后中`
- 售后工单关闭后，命中的原销售订单行会推进为 `已关闭`，订单头再按整单行状态重新聚合
- 已补 `After Sales Ticket.on_update` 回刷，工单状态变化时会自动重算原单与补发单的销售订单履约状态

### T441 售后与库存闭环增强

| 项目 | 内容 |
|---|---|
| 任务编号 | `T441` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 自动补日志、补状态建议、补结案条件 |
| 交付物 | 售后与库存状态增强逻辑 |

当前实现说明：

- 售后服务已支持系统日志自动补全
- `apply_decision` 已具备处理结论状态建议
- `close_ticket` 已校验退款完成、补发单存在等结案条件
- 本任务实际已被现有售后服务提前承接

### T450 运营报表

| 项目 | 内容 |
|---|---|
| 任务编号 | `T450` |
| 优先级 | `P1` |
| 状态 | `TODO` |
| 目标 | 输出运营核心报表 |
| 交付物 | 报表或 Workspace 看板 |

建议先做：

- 款号库存报表
- 原辅料库存与备货报表
- 到货与入库报表
- 订单履约状态报表
- 售后状态报表

### T451 财务与成本报表

| 项目 | 内容 |
|---|---|
| 任务编号 | `T451` |
| 优先级 | `P1` |
| 状态 | `TODO` |
| 目标 | 输出预计成本、采购/外包和经营相关报表 |
| 交付物 | 财务分析报表、履约成本分析 |

### T460 测试基础设施与首批单元测试

| 项目 | 内容 |
|---|---|
| 任务编号 | `T460` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 建立正式测试基础设施并覆盖核心工具函数与服务函数 |
| 交付物 | 测试目录、mock 策略、首批单元测试用例 |

建议首批覆盖：

- `style_service.py`
- `stock_service.py`
- `after_sales_service.py`
- `outsource_service.py`
- `outsource_receipt_service.py`

当前实现说明：

- 已新增 `custom_apps/fashion_erp/tests/unit` 作为业务单元测试目录
- 已提供 fake `frappe` 的轻量测试基座，可在无完整 Frappe 运行时的环境下导入服务模块
- 已补首批单元测试，覆盖 `style_service.py`、`stock_service.py`、`after_sales_service.py`、`supply_service.py`、`outsource_service.py`、`outsource_receipt_service.py`
- 当前本地执行口径为 `python3 -m unittest discover -s custom_apps/fashion_erp/tests/unit -p 'test_*.py'`

### T461 状态机与集成测试

| 项目 | 内容 |
|---|---|
| 任务编号 | `T461` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 补齐关键状态流转和集成流程测试 |
| 交付物 | 状态机测试、seed 幂等性测试、关键业务集成测试 |

建议优先覆盖：

- 库存状态流转
- 售后工单状态流转
- 外包单 / 外包到货单状态流转
- SKU 生成完整流程

当前实现说明：

- 已补 `Outsource Order` 状态推进与非法取消回归测试
- 已补 `Outsource Receipt` 从收货到质检完成的状态链测试，以及已入库/已质检后的取消拦截测试
- 已补 `After Sales Ticket` 的退款主链测试，以及待补发未生成补发单时的关闭拦截测试
- 已补 `seed_stock_master_data` 幂等性测试与 `generate_variants_for_style` 的创建/更新/跳过主流程测试
- 当前执行口径仍为 `python3 -m unittest discover -s custom_apps/fashion_erp/tests/unit -p 'test_*.py'`

### T462 性能与数据访问收口

| 项目 | 内容 |
|---|---|
| 任务编号 | `T462` |
| 优先级 | `P1` |
| 状态 | `DONE` |
| 目标 | 收口当前明显的 N+1 查询和重复加载问题 |
| 交付物 | SKU 批量预加载、矩阵批量查询、API/Service 重复加载消除 |

当前实现说明：

- 已先收一层 `After Sales Ticket` 明细校验的重复加载，`after_sales_service` 现已对 `Sales Order Item / Delivery Note Item / Item / Return Disposition` 做请求级缓存
- 已补 `order_sync_service` 的批次级缓存，批量校验重复 `Customer / Item / Warehouse / Price List` 链接时不再重复查库；构建 `Sales Order` 明细时对重复 SKU 的冗余字段读取也已缓存
- 已补 `sku_service.build_style_matrix` 的批量查询，矩阵加载时改为批量拉取 `Item` 与 `Bin`，不再按每个款色码组合逐个读取货品和库存
- 已补 `sku_service.generate_variants_for_style` 的批量预取，当前会复用同一批尺码列表和品牌简称，并先批量查询已存在 SKU，再决定创建/更新/跳过
- 已补 `outsource_service` 的单据级缓存，外包单材料归一化时对重复 `Item / Warehouse / Warehouse Location` 链接和物料主数据读取不再逐行重复执行；提交前的 `Craft Sheet` 状态读取也已复用
- 已补 `sample_service / craft_sheet_service` 的单据级缓存，当前会复用 `Style / Sample Ticket / Color / Color Group` 元数据，以及重复 `User` 链接校验，减少打样单和工艺单保存时的重复读取
- 已补 `sales_order_fulfillment_service` 的售后上下文批量读取，销售订单聚合履约状态时改为一次查询工单头、一次查询工单明细，不再逐张 `After Sales Ticket` 加载整单
- 已补 `after_sales_ticket` 事件的父单与订单存在性批量读取，售后工单回刷关联销售订单时改为一次查询 `Sales Order Item -> parent` 映射，并批量确认 `Sales Order` 存在性，不再按售后明细和销售订单逐条读取
- 已补 `sales_order` 事件的售后补发回写轻量读取，销售订单回写 `After Sales Ticket.replacement_sales_order` 时改为先做一次轻量字段查询，只有需要更新时才加载整张工单
- 已补 `bom / work_order` 事件的生产跟踪单轻量回写，物料清单和生产工单同步 `Production Ticket` 时改为先检查轻量字段，只有确实需要回写时才加载整单
- 已补 `style.api + sku_service` 的款号复用，模板货品创建、单品生成、款色码矩阵接口在 API 层加载 `Style` 后会直接传给服务层，不再按同一 `style_name` 二次加载
- 已补 `after_sales_service` 的售后头信息缓存，同一工单上下文里的 `Sales Order / Sales Invoice / Delivery Note / Channel Store / Warehouse Location` 头字段同步与公司/交期推导会复用同一批读取结果
- 已补 `after_sales_service` 的补发行与库存凭证缓存，补发单草稿行会复用同一次工单校验里已加载的 `Sales Order Item`，默认公司和 `Stock Entry Type` 也改为请求级复用
- 已补 `supply_service` 的单据级缓存，采购/收货校验时对重复 `Supplier / Item / Purchase Order Item / Sample Ticket / Warehouse Location` 的读取与链接校验不再逐行重复执行
- 已补 `outsource_receipt_service` 的单据级缓存，外包到货单同步外包单头、库位仓库、到货货品主数据和操作人链接时，重复读取会在同一次校验上下文内复用
- 已补 `production_service` 的单据级缓存，生产跟踪单校验 `BOM / Work Order / Style` 时会复用链接存在性，并改为一次性读取引用字段；默认公司、引用单据公司与 `Stock Entry Type` 也已改成同一上下文复用
- 已补 `delivery_note_fulfillment_service` 的单据级缓存，出货单校验包装耗材时对重复 `Item` 主数据和 `Warehouse` 链接校验不再逐行重复执行
- 已补针对重复 `sales_order_item_ref / item_code` 的单元测试，确认同一次校验过程中不会重复读取同一主数据
- 结论：当前业务主线上的明显 N+1 和重复加载热点已完成收口；后续若出现新的报表查询优化需求，转入 `T450/T451` 对应实现时单独处理

说明：

- 这是技术债任务，不抢在业务主线前面
- 优先采用批量查询和字典映射，不急着一开始就写重 SQL

### T490 内部生产深化后置

| 项目 | 内容 |
|---|---|
| 任务编号 | `T490` |
| 优先级 | `P2` |
| 状态 | `TODO` |
| 目标 | 在打样辅助之外，再决定是否扩展内部生产 |
| 交付物 | 后续决策结论 |

## 剩余建议顺序

经核对当前代码仓：

- `T405-T421`、`T441`、`T460-T461` 与文档状态基本一致
- `T430/T431` 已完成基础版，已具备批次导入、预览执行、去重规则、CSV 粘贴导入和索引 patch
- `T432` 已完成基础版，已具备订单头/订单行履约状态字段、保存时聚合推进规则，以及 `Delivery Note` 发货/撤销发货回刷
- `T433` 已完成基础版，已具备销售订单履约动作入口、状态推进，以及 `Delivery Note` 草稿生成
- `T434` 已完成基础版，已具备出货单耗材子表、包装耗材校验、耗材估算金额汇总和 `Stock Entry(Material Issue)` 草稿生成
- `T435` 已完成基础版，已具备快递费字段、履约总成本汇总和履约成本汇总接口
- `T422` 已完成基础版，已具备外包到货异常字段、异常汇总和零到货短装留痕规则
- `T440` 已完成基础版，已具备售后工单驱动的订单头/订单行闭环状态回写

1. `T450`
2. `T451`
3. `T490`
