import {T as W} from "./templateParser-B5n_xv6p.js";
import {$ as a, L as e, d as I, q as $, G as R, c as m, b as s, z as n, I as H, h as p, _ as M, E as D, N as b, C as U, g as B, W as v, a5 as h, u as S, ar as F, aq as O, F as V, d7 as C, bI as A, e as P} from "./i18n-qmGvp-Y0.js";
import {d as Y} from "./dayjs.min-C4S9edGi.js";
import {_ as x} from "./index-HEOtdw79.js";
const c = new Map;
c.set(1, {
    background: "blue",
    tagColor: () => "primary",
    tagText: () => a("layout.message.SHIPPING"),
    getThemeColor: () => "colorPrimary"
});
c.set(2, {
    background: "red",
    tagColor: () => "bad",
    tagText: () => a("layout.message.ESCAPE"),
    getThemeColor: () => "colorError"
});
c.set(3, {
    background: "green",
    tagColor: () => "success",
    tagText: () => a("layout.message.INCREASE"),
    getThemeColor: () => "colorSuccess"
});
c.set(4, {
    background: "red",
    tagColor: () => "bad",
    tagText: () => a("layout.message.REDUCE"),
    getThemeColor: () => "colorError"
});
c.set(5, {
    background: "blue",
    tagColor: T => "success",
    tagText: T => Number(T.scoring) > 55 ? a("layout.message.ADD_CHANCE1") : a("layout.message.ADD_CHANCE2"),
    getThemeColor: T => Number(T.scoring) > 55 ? "colorSuccess" : "#7ab600"
});
c.set(6, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.QUIT_CHANCE"),
    getThemeColor: () => "colorError"
});
c.set(7, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.DOWNSIDE_RISK"),
    getThemeColor: () => "colorError"
});
c.set(8, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.QUIT_CHANCE"),
    getThemeColor: () => "colorError"
});
c.set(18, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.QUIT_CHANCE"),
    getThemeColor: () => "colorError"
});
c.set(16, {
    background: "green",
    tagColor: () => "success",
    tagText: () => a("layout.message.GAINS"),
    getThemeColor: () => "colorSuccess"
});
c.set(17, {
    background: "red",
    tagColor: () => "bad",
    tagText: () => a("layout.message.DRAWDOWN"),
    getThemeColor: () => "colorError"
});
c.set(19, {
    background: "red",
    tagColor: () => "success",
    tagText: () => a("layout.message.DRAWDOWN"),
    getThemeColor: () => "colorSuccess"
});
c.set(22, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.REBOUND_AFTER_DROP"),
    getThemeColor: () => "colorError"
});
c.set(23, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.REBOUND_AFTER_DROP"),
    getThemeColor: () => "colorError"
});
c.set(24, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.DOWNSIDE_RISK"),
    getThemeColor: () => "colorError"
});
c.set(25, {
    background: "blue",
    tagColor: () => "primary",
    tagText: () => a("common.capitalMovement"),
    getThemeColor: () => "colorSuccess"
});
c.set(27, {
    background: "blue",
    tagColor: () => "primary",
    tagText: () => a("common.capitalMovement"),
    getThemeColor: () => "colorSuccess"
});
c.set(28, {
    background: "blue",
    tagColor: () => "warning",
    tagText: () => a("layout.message.ACCELERATE_ACCUMULATION"),
    getThemeColor: () => "colorSuccess"
});
c.set(29, {
    background: "blue",
    tagColor: () => "warning",
    tagText: () => a("layout.message.DISTRIBUTION_ACCELERATING"),
    getThemeColor: () => "colorSuccess"
});
c.set(30, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.PROTECT_YOUR_CAPITAL"),
    getThemeColor: () => "colorSuccess"
});
c.set(31, {
    background: "blue",
    tagColor: () => "bad",
    tagText: () => a("layout.message.PROTECT_YOUR_CAPITAL"),
    getThemeColor: () => "colorSuccess"
});
const l = new Map;
l.set(1, {
    title: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    },
    content: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    }
});
l.set(2, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 风险增加，大部分止盈以保护利润",
        [e.ZH_TW]: "{{symbolStyle}} 風險增加，大部分止盈以保護利潤",
        [e.EN]: "{{symbolStyle}} risk increases, most of the stop profits to protect profits"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力大量减持，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力大量減持，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，留意市場風險。",
        [e.EN]: "{{symbolStyle}} suspected main force reduced holdings, now reported {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, pay attention to market risks."
    }
});
l.set(3, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力增持，注意市场变化",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力增持，留意市場變化",
        [e.EN]: "{{symbolStyle}} is suspected to be the whales to increase holdings, pay attention to market risks"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力持仓增加，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，市场情绪乐观，但需注意高抛风险。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力持倉增加，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，市場情緒樂觀，但需留意高拋風險。",
        [e.EN]: "{{symbolStyle}}'s net capital inflow in CEX has increased, the price is {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, market sentiment is optimistic, but pay attention to the risk of high selling."
    }
});
l.set(4, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力减持，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力減持，留意市場風險",
        [e.EN]: "{{symbolStyle}} is suspected to be the whales to reduce holdings, pay attention to market risks"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力持仓减少，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力持倉減少，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，留意市場風險。",
        [e.EN]: "{{symbolStyle}} suspected main force holdings decreased, now reported {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, pay attention to market risks."
    }
});
l.set(5, {
    title: {
        [e.ZH_CN]: "AI捕获疑似有潜力的代币，开始实时追踪 {{symbolStyle}}",
        [e.ZH_TW]: "AI捕捉疑似有潛力的代幣，開始即時追蹤 {{symbolStyle}}",
        [e.EN]: "AI captures suspected potential tokens and starts tracking {{symbolStyle}} in real-time"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，当前AI评分{{scoringStyle}}，请注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，當前AI評分{{scoringStyle}}，請注意市場風險。",
        [e.EN]: "{{symbolStyle}} is currently priced at {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, current AI score {{scoringStyle}}, please pay attention to market risks."
    }
});
l.set(6, {
    title: {
        [e.ZH_CN]: "AI实时追踪 {{symbolStyle}} 结束，注意市场风险",
        [e.ZH_TW]: "AI即時追蹤 {{symbolStyle}} 結束，留意市場風險",
        [e.EN]: "AI real-time tracking of {{symbolStyle}} ends, please pay attention to market risks"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，当前AI评分{{scoringStyle}}，请注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，當前AI評分{{scoringStyle}}，請注意市場風險。",
        [e.EN]: "{{symbolStyle}} is currently priced at {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, current AI score {{scoringStyle}}, pay attention to market risks."
    }
});
l.set(7, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 风险增加，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 風險增加，註意市場風險",
        [e.EN]: "{{symbolStyle}} Risk Increased"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力大量减持，价格有下跌风险，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，大部分止盈以保护利润。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力大量減持，價格有下跌風險，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，大部分止盈以保護利潤。",
        [e.EN]: "Large-scale {{symbolStyle}} outflow detected. Price may face downward pressure. Current price: {{priceStyle}}, {{enUpDownStyle}} of {{percentChange24hStyle}}. Majority of positions partially closed."
    }
});
l.set(8, {
    title: {
        [e.ZH_CN]: "AI实时追踪 {{symbolStyle}} 结束，注意市场风险",
        [e.ZH_TW]: "AI實時追蹤 {{symbolStyle}} 結束，註意市場風險",
        [e.EN]: "{{symbolStyle}} Tracking Ended"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}}价格下跌趋势减弱，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，AI实时追踪结束，请注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}}價格下跌趨勢減弱，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，AI實時追蹤結束，請註意市場風險。",
        [e.EN]: "{{symbolStyle}} downtrend has slowed. Current price: {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}. Real-time tracking ended."
    }
});
l.set(16, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪后的涨幅超过{{gainsStyle}}，移动止盈以保护利润",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤後的漲幅超過{{gainsStyle}}，移動止盈以保護利潤",
        [e.EN]: "{{symbolStyle}} tracking increase of more than {{gainsStyle}}, move the stop profit to protect profits"
    },
    content: {
        [e.ZH_CN]: "AI追踪后涨幅{{gainsStyle}}，现报{{priceStyle}}，注意移动止盈以保护利润。",
        [e.ZH_TW]: "AI追蹤後漲幅{{gainsStyle}}，現報{{priceStyle}}，留意移動止盈以保護利潤。",
        [e.EN]: "AI tracking increase of {{gainsStyle}}, the current price is {{priceStyle}}, pay attention to move the stop profit to protect profits."
    }
});
l.set(17, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪达到最大涨幅后，跌幅超过{{declineStyle}}，移动止盈以保护利润",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤達到最大漲幅後，跌幅超過{{declineStyle}}，移動止盈以保護利潤",
        [e.EN]: "{{symbolStyle}} fell more than {{declineStyle}} after tracking, move the stop profit to protect profits"
    },
    content: {
        [e.ZH_CN]: "AI 追踪后上涨，达到最大涨幅后下跌，跌幅超过{{declineStyle}}，现报{{priceStyle}}，注意移动止盈以保护利润。",
        [e.ZH_TW]: "AI 追蹤後上漲，達到最大漲幅後下跌，跌幅超過{{declineStyle}}，現報{{priceStyle}}，留意移動止盈以保護利潤。",
        [e.EN]: "AI rose after tracking, and the decline after the rise was {{declineStyle}}, and the current price is {{priceStyle}}. Pay attention to moving the stop profit to protect profits."
    }
});
l.set(18, {
    title: {
        [e.ZH_CN]: "AI实时追踪 {{symbolStyle}} 结束，注意市场风险",
        [e.ZH_TW]: "AI即時追蹤 {{symbolStyle}} 結束，留意市場風險",
        [e.EN]: "AI real-time tracking of {{symbolStyle}} ends, please pay attention to market risks"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 现报{{priceStyle}}，AI追踪期间最大涨幅{{gainsStyle}}，AI追踪已结束，注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 現報{{priceStyle}}，AI追蹤期間最大漲幅{{gainsStyle}}，AI追蹤已結束，留意市場風險。",
        [e.EN]: "{{symbolStyle}} is currently priced at {{priceStyle}},the max gain tracked by AI is {{gainsStyle}}. AI tracking has ended, please pay attention to market risks."
    }
});
l.set(19, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪后的跌幅超过{{riskDeclineStyle}}，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤後的跌幅超過{{riskDeclineStyle}}，註意市場風險",
        [e.EN]: "{{symbolStyle}} Dropped Over {{riskDeclineStyle}} Since Tracking Started"
    },
    content: {
        [e.ZH_CN]: "AI追踪后下跌，且跌幅超过{{riskDeclineStyle}}，现报{{priceStyle}}，移动止盈以保护利润。",
        [e.ZH_TW]: "AI追蹤後下跌，且跌幅超過{{riskDeclineStyle}}，現報{{priceStyle}}，移動止盈以保護利潤。",
        [e.EN]: "{{symbolStyle}} price declined over {{riskDeclineStyle}} after tracking began. Current price: {{priceStyle}}. Trailing take-profit triggered."
    }
});
l.set(20, {
    title: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    },
    content: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    }
});
l.set(21, {
    title: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    },
    content: {
        [e.ZH_CN]: "",
        [e.ZH_TW]: "",
        [e.EN]: ""
    }
});
l.set(22, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪下跌后反弹，且反弹涨幅超过{{reboundStyle}}，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤下跌後反彈，且反彈漲幅超過{{reboundStyle}}，註意市場風險",
        [e.EN]: "{{symbolStyle}} Rebounded Over {{reboundStyle}} After Decline"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}}下跌幅度超过{{riskDeclineStyle}}，且触底后反弹超过{{reboundStyle}}，移动止盈以保护利润。",
        [e.ZH_TW]: "{{symbolStyle}}下跌幅度超過{{riskDeclineStyle}}，且觸底後反彈超過{{reboundStyle}}，移動止盈以保護利潤。",
        [e.EN]: "{{symbolStyle}} declined over {{riskDeclineStyle}}, then rebounded more than {{reboundStyle}} from the low. Trailing take-profit triggered."
    }
});
l.set(23, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪下跌后反弹，且反弹涨幅超过{{reboundStyle}}，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤下跌後反彈，且反彈漲幅超過{{reboundStyle}}，註意市場風險",
        [e.EN]: "{{symbolStyle}} Rebounded Over {{reboundStyle}} After Decline"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}}下跌幅度超过{{riskDeclineStyle}}，且触底后反弹超过{{reboundStyle}}，大部分止盈以保护利润。",
        [e.ZH_TW]: "{{symbolStyle}}下跌幅度超過{{riskDeclineStyle}}，且觸底後反彈超過{{reboundStyle}}，大部分止盈以保護利潤。",
        [e.EN]: "{{symbolStyle}} declined over {{riskDeclineStyle}}, then rebounded more than {{reboundStyle}} from the low. Majority take-profit triggered."
    }
});
l.set(24, {
    title: {
        [e.ZH_CN]: "AI捕获疑似价格高点的代币，开始实时追踪 {{symbolStyle}}",
        [e.ZH_TW]: "AI捕獲疑似價格高點的代幣，開始實時追蹤 {{symbolStyle}}",
        [e.EN]: "Token Detected Near Potential Price Peak and starts tracking {{symbolStyle}} in real-time"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，请注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，請註意市場風險。",
        [e.EN]: "{{symbolStyle}} current price: {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}. Real-time tracking initiated."
    }
});
l.set(25, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 24H内{{tradeType}}资金异动，请重点关注",
        [e.ZH_TW]: "{{symbolStyle}} 24H内{{tradeType}}資金異動，請重點關註",
        [e.EN]: "{{symbolStyle}} {{tradeType}} Funds Shift (24H): High Alert!"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 在24H内出现大量{{tradeType}}资金异常流入，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，请注意市场行情变化。",
        [e.ZH_TW]: "{{symbolStyle}} 在24H內出現大量{{tradeType}}資金異常流入，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，請註意市場行情變化。",
        [e.EN]: "Significant unusual inflow detected in {{symbolStyle}} {{tradeType}} funds within 24 hours. now reported {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, Monitor market conditions closely."
    }
});
l.set(27, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 24H外{{tradeType}}资金异动，请重点关注",
        [e.ZH_TW]: "{{symbolStyle}} 24H外{{tradeType}}資金異動，請重點關註",
        [e.EN]: "{{symbolStyle}} {{tradeType}} Funds Shift (Outside 24H): High Alert!"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 在24H外出现大量{{tradeType}}资金异常流入，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，请注意市场行情变化。",
        [e.ZH_TW]: "{{symbolStyle}} 在24H外出現大量{{tradeType}}資金異常流入，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，請註意市場行情變化。",
        [e.EN]: "Significant atypical inflow detected in {{symbolStyle}} {{tradeType}} funds beyond 24-hour window. now reported {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}, Expect heightened volatility."
    }
});
l.set(28, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力增持加速，可能有上涨行情，注意市场变化",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力增持加速，可能有上漲行情，注意市場變化",
        [e.EN]: "{{symbolStyle}} Whale Accumulation Accelerating – Upside Potential"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力大量买入中，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，市场情绪乐观，但需注意高抛风险。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力大量買入中，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，市場情緒樂觀，但需注意高拋風險。",
        [e.EN]: "{{symbolStyle}} appears to be under heavy accumulation by whales. Current price: {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}. Market sentiment is optimistic, but be cautious of potential profit-taking risks."
    }
});
l.set(29, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力持仓减少加速，价格可能下跌，注意市场风险",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力持倉減少加速，價格可能下跌，注意市場風險",
        [e.EN]: "{{symbolStyle}} Whale Distribution Accelerating – Downside Risk"
    },
    content: {
        [e.ZH_CN]: "{{symbolStyle}} 疑似主力大量抛售，现报{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，注意市场风险。",
        [e.ZH_TW]: "{{symbolStyle}} 疑似主力大量拋售，現報{{priceStyle}}，24H{{cnUpDownStyle}}{{percentChange24hStyle}}，注意市場風險。",
        [e.EN]: "{{symbolStyle}} appears to be under heavy selling pressure from whales. Current price: {{priceStyle}}, 24H {{enUpDownStyle}} of {{percentChange24hStyle}}. Market risk is rising – proceed with caution."
    }
});
l.set(30, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪后的涨幅超过{{gainsStyle}}，注意保护本金",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤後的漲幅超過{{gainsStyle}}，注意保護本金",
        [e.EN]: "{{symbolStyle}} tracking increase of more than {{gainsStyle}}, Protect Your Capital"
    },
    content: {
        [e.ZH_CN]: "AI追踪后涨幅{{gainsStyle}}，现报{{priceStyle}}，注意保护本金。",
        [e.ZH_TW]: "AI追蹤後漲幅{{gainsStyle}}，現報{{priceStyle}}，注意保護本金。",
        [e.EN]: "AI tracking increase of {{gainsStyle}}, the current price is {{priceStyle}}. Consider taking measures to protect your capital."
    }
});
l.set(31, {
    title: {
        [e.ZH_CN]: "{{symbolStyle}} 追踪后的跌幅超过{{riskDeclineStyle}}，注意保护本金",
        [e.ZH_TW]: "{{symbolStyle}} 追蹤後的跌幅超過{{riskDeclineStyle}}，注意保護本金",
        [e.EN]: "{{symbolStyle}} Dropped Over {{riskDeclineStyle}} Since Tracking Started, Protect Your Capital"
    },
    content: {
        [e.ZH_CN]: "AI追踪后下跌，且幅度超过{{riskDeclineStyle}}，现报{{priceStyle}}，注意保护本金。",
        [e.ZH_TW]: "AI追蹤後下跌，且幅度超過{{riskDeclineStyle}}，現報{{priceStyle}}，注意保護本金。",
        [e.EN]: "{{symbolStyle}} price declined over {{riskDeclineStyle}} after tracking began. Current price: {{priceStyle}}. Consider taking measures to protect your capital."
    }
});
const Q = {
    class: "warn-track-message"
}
  , j = I({
    __name: "WarnTrackMessage",
    props: {
        data: {},
        ableToDetail: {
            type: Boolean,
            default: !0
        }
    },
    emits: ["toDetail"],
    setup(T, {emit: r}) {
        const t = T
          , N = r
          , _ = $()
          , g = R( () => _.language);
        async function f() {
            t.ableToDetail && N("toDetail", t.data.keyword)
        }
        function Z() {
            if (!l.has(t.data.predictType))
                return s("div", null, null);
            const i = new W(l.get(t.data.predictType).title[g.value]);
            return i.setStrategy("symbolStyle", () => s("span", {
                class: t.ableToDetail ? "color-primary cursor-pointer" : "",
                onClick: f
            }, [t.data.symbol])),
            i.setStrategy("percentChange24hStyle", () => {
                const d = Number(Number(t.data.percentChange24h).toFixed(2));
                return s("span", {
                    class: "text-nowrap"
                }, [Math.abs(d), n("%")])
            }
            ),
            i.setStrategy("reboundStyle", () => {
                const d = Math.abs(Number(Number(t.data.rebound).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("gainsStyle", () => {
                const d = Math.abs(Number(Number(t.data.gains).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("declineStyle", () => {
                const d = Math.abs(Number(Number(t.data.decline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("riskDeclineStyle", () => {
                const d = Math.abs(Number(Number(t.data.riskDecline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("tradeType", () => {
                if (t.data.tradeType === 1)
                    return a("common.spot");
                if (t.data.tradeType === 2)
                    return a("common.futures")
            }
            ),
            i.parser()
        }
        function w() {
            if (!l.has(t.data.predictType))
                return s("div", null, null);
            const i = new W(l.get(t.data.predictType).content[g.value]);
            return i.setStrategy("symbolStyle", () => t.data.symbol),
            i.setStrategy("priceStyle", () => s("span", {
                class: "color-primary"
            }, [n("$"), H(t.data.price).toPrice()])),
            i.setStrategy("cnUpDownStyle", () => g.value === e.ZH_CN ? t.data.percentChange24h >= 0 ? "涨幅" : "跌幅" : g.value === e.ZH_TW ? t.data.percentChange24h >= 0 ? "漲幅" : "跌幅" : ""),
            i.setStrategy("percentChange24hStyle", () => {
                const d = Number(Number(t.data.percentChange24h).toFixed(2));
                return s("span", {
                    class: "text-nowrap"
                }, [Math.abs(d), n("%")])
            }
            ),
            i.setStrategy("scoringStyle", () => t.data.scoring),
            i.setStrategy("gradeStyle", () => t.data.grade),
            i.setStrategy("enUpDownStyle", () => t.data.percentChange24h >= 0 ? "increase" : "drop"),
            i.setStrategy("riskDeclineStyle", () => {
                const d = Math.abs(Number(Number(t.data.riskDecline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("reboundStyle", () => {
                const d = Math.abs(Number(Number(t.data.rebound).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("gainsStyle", () => {
                const d = Math.abs(Number(Number(t.data.gains).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("declineStyle", () => {
                const d = Math.abs(Number(Number(t.data.decline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [d, n("%")])
            }
            ),
            i.setStrategy("tradeType", () => {
                if (t.data.tradeType === 1)
                    return a("common.spot");
                if (t.data.tradeType === 2)
                    return a("common.futures")
            }
            ),
            i.parser()
        }
        return (i, d) => (p(),
        m("div", Q, [s(Z, {
            class: "title"
        }), s(w, {
            class: "content"
        })]))
    }
})
  , Ce = M(j, [["__scopeId", "data-v-5885c07b"]]);
function K(T) {
    switch (T) {
    case 1:
        return {
            title: a("route.Quality"),
            icon: s(D, {
                color: "var(--color-success)"
            }, {
                default: () => [s(x, {
                    src: "message/warn-long",
                    fill: "currentColor"
                }, null)]
            })
        };
    case 2:
        return {
            title: a("route.Risk"),
            icon: s(D, {
                color: "var(--color-error)"
            }, {
                default: () => [s(x, {
                    src: "message/warn-short"
                }, null)]
            })
        };
    case 3:
        return {
            title: a("route.CapitalMovement"),
            icon: s(D, {
                color: "#FFC037"
            }, {
                default: () => [s(x, {
                    src: "message/warn-alert"
                }, null)]
            })
        };
    default:
        return {
            title: "",
            icon: "!"
        }
    }
}
const z = {
    class: "warn-message-tags flex gap-8px"
}
  , X = {
    key: 0,
    class: "alpha-tag"
}
  , q = {
    class: "alpha-tag_symbol"
}
  , J = {
    key: 1,
    class: "tag tag-coin"
}
  , ee = {
    key: 0,
    class: "tag tag-inside"
}
  , te = {
    key: 1,
    class: "tag tag-outside"
}
  , ae = {
    key: 0,
    class: "tag tag-spot"
}
  , se = {
    key: 1,
    class: "tag tag-futures"
}
  , re = I({
    __name: "WarnTrackMessageTags",
    props: {
        data: {},
        showScore: {
            type: Boolean,
            default: !0
        },
        showRiskLevel: {
            type: Boolean,
            default: !0
        },
        showPredictType: {
            type: Boolean,
            default: !0
        },
        showTradeType: {
            type: Boolean,
            default: !0
        },
        observe: {
            type: Boolean,
            default: !1
        },
        messageType: {}
    },
    setup(T) {
        const r = T;
        function t(_) {
            switch (Number(_)) {
            case 1:
                return "success";
            case 2:
                return "grade1";
            case 3:
                return "grade2";
            case 4:
                return "error";
            default:
                return "primary"
            }
        }
        function N() {
            const _ = K(r.messageType);
            return s("div", {
                class: "flex flex-items-center gap-4px"
            }, [s(D, {
                size: 12
            }, {
                default: () => [_.icon]
            }), _.title])
        }
        return (_, g) => (p(),
        m("div", z, [r.data.symbol && r.observe ? (p(),
        m("div", X, [g[0] || (g[0] = v("div", {
            class: "alpha-tag_alpha"
        }, [n(" Alpha "), v("div", {
            class: "alpha-tag_circle top"
        }), v("div", {
            class: "alpha-tag_circle bottom"
        })], -1)), v("div", q, h(S(F)(r.data.symbol, 5)), 1)])) : r.data.symbol ? (p(),
        m("div", J, h(S(F)(r.data.symbol, 5)), 1)) : b("", !0), r.showPredictType ? U(_.$slots, "predictType", {
            key: 2
        }, () => {
            var f, Z;
            return [r.data.predictType === 25 ? (p(),
            m("div", ee, h(S(a)("common.Inside24H")), 1)) : r.data.predictType === 27 ? (p(),
            m("div", te, h(S(a)("common.Outside24H")), 1)) : S(c).has(r.data.predictType) ? (p(),
            m("div", {
                key: 2,
                class: O(["tag", `tag-${(f = S(c).get(r.data.predictType)) == null ? void 0 : f.tagColor(r.data)}`])
            }, h((Z = S(c).get(r.data.predictType)) == null ? void 0 : Z.tagText(r.data)), 3)) : b("", !0)]
        }
        , !0) : b("", !0), r.showScore && r.data.scoring && r.data.grade ? (p(),
        m("div", {
            key: 3,
            class: O(["tag", `tag-${t(r.data.grade)}`])
        }, h(S(a)("common.AIScore")) + ": " + h(r.data.scoring), 3)) : b("", !0), r.showTradeType ? (p(),
        m(V, {
            key: 4
        }, [r.data.tradeType === 1 ? (p(),
        m("div", ae, h(S(a)("layout.spot")), 1)) : r.data.tradeType === 2 ? (p(),
        m("div", se, h(S(a)("layout.futures")), 1)) : b("", !0)], 64)) : b("", !0), U(_.$slots, "other", {}, void 0, !0), r.messageType ? (p(),
        B(N, {
            key: 5,
            class: "ml-auto"
        })) : b("", !0)]))
    }
})
  , oe = M(re, [["__scopeId", "data-v-6b882417"]])
  , u = new Map;
u.set(101, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{tradeType}}最大资金净流入达{{total}}",
        [e.ZH_TW]: "{{symbol}}{{tradeType}}最大資金凈流入達{{total}}",
        [e.EN]: "{{symbol}} {{tradeType}} Net Inflow Reached {{total}}"
    },
    content: {
        [e.ZH_CN]: "{{symbol}}现报{{price}}，{{tradeType}}{{times}}净流入资金达到{{total}}，涨幅达{{change}}",
        [e.ZH_TW]: "{{symbol}}現報{{price}}，{{tradeType}}{{times}}凈流入資金達到{{total}}，漲幅達{{change}}",
        [e.EN]: "{{symbol}} is currently trading at {{price}}. The {{tradeType}} net inflow during the {{times}} reached {{total}}, with a maximum surge of {{change}}."
    }
});
u.set(-101, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{tradeType}}最大资金净流入跌至{{total}}",
        [e.ZH_TW]: "{{symbol}}{{tradeType}}最大資金凈流入跌至{{total}}",
        [e.EN]: "{{symbol}} {{tradeType}} Net Inflow Reached {{total}}"
    },
    content: {
        [e.ZH_CN]: "{{symbol}}现报{{price}}，{{tradeType}}{{times}}净流入资金跌至{{total}}，跌幅达{{change}}",
        [e.ZH_TW]: "{{symbol}}現報{{price}}，{{tradeType}}{{times}}凈流入資金跌至{{total}}，跌幅達{{change}}",
        [e.EN]: "{{symbol}} is currently trading at {{price}}. The {{tradeType}} net inflow during the {{times}} reached {{total}}, with a maximum surge of {{change}}."
    }
});
u.set(107, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{tradeType}}最大交易量涨幅突破{{change}}",
        [e.ZH_TW]: "{{symbol}}{{tradeType}}最大交易量漲幅突破{{change}}",
        [e.EN]: "{{symbol}} {{tradeType}} Surges with Max Volume Increase of {{change}}"
    },
    content: {
        [e.ZH_CN]: "{{symbol}}现报{{price}}，{{tradeType}}{{times}}交易量涨幅达{{change}}",
        [e.ZH_TW]: "{{symbol}}現報{{price}}，{{tradeType}}{{times}}交易量漲幅達{{change}}",
        [e.EN]: "{{symbol}} is currently trading at {{price}}. {{tradeType}} volume over {{times}} increased by {{change}}."
    }
});
u.set(-107, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{tradeType}}最大交易量跌幅突破{{change}}",
        [e.ZH_TW]: "{{symbol}}{{tradeType}}最大交易量跌幅突破{{change}}",
        [e.EN]: "{{symbol}} {{tradeType}} Surges with Max Volume Increase of {{change}}"
    },
    content: {
        [e.ZH_CN]: "{{symbol}}现报{{price}}，{{tradeType}}{{times}}交易量跌幅达{{change}}",
        [e.ZH_TW]: "{{symbol}}現報{{price}}，{{tradeType}}{{times}}交易量跌幅達{{change}}",
        [e.EN]: "{{symbol}} is currently trading at {{price}}. {{tradeType}} volume over {{times}} dropped by {{change}}."
    }
});
u.set(103, {
    title: {
        [e.ZH_CN]: "{{symbol}}发生大额交易,价值约{{value}}",
        [e.ZH_TW]: "{{symbol}}發生大額交易,價值約{{value}}",
        [e.EN]: "Large Transaction Detected in {{symbol}}, Estimated Value ~{{value}}"
    },
    content: {
        [e.ZH_CN]: "{{updateTime}}，发生一笔鲸鱼转账，数量为{{amount}}{{symbol}}（价值约{{value}}），交易哈希：{{tradeHash}}",
        [e.ZH_TW]: "{{updateTime}}，發生一筆鯨魚轉賬，數量為{{amount}}{{symbol}}（價值約{{value}}），交易哈希：{{tradeHash}}",
        [e.EN]: "At {{updateTime}}, a whale transaction of {{amount}} {{symbol}} was detected (~{{value}}). Transaction Hash:{{tradeHash}}"
    }
});
u.set(104, {
    title: {
        [e.ZH_CN]: "{{address}}发生大额转账",
        [e.ZH_TW]: "{{address}}發生大額轉賬",
        [e.EN]: "Large [Outbound/Inbound] Transaction to {{address}}"
    },
    content: {
        [e.ZH_CN]: "{{fromAddress}}于 {{updateTime}}{{flow}}{{toAddress}}{{action}}{{amount}}{{symbol}}（价值约{{value}}），交易哈希{{tradeHash}}",
        [e.ZH_TW]: "{{fromAddress}}於 {{updateTime}}{{flow}}{{toAddress}}{{action}}{{amount}}{{symbol}}（價值約{{value}}），交易哈希{{tradeHash}}",
        [e.EN]: "{{fromAddress}} transferred {{amount}} {{symbol}} (~{{value}}) {{flow}} {{toAddress}} at {{updateTime}}. Transaction Hash: {{tradeHash}}"
    }
});
u.set(105, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{timeType}}：{{threshold}}",
        [e.ZH_TW]: "{{symbol}}{{timeType}}：{{threshold}}",
        [e.EN]: "{{symbol}}{{timeType}} at {{threshold}}"
    },
    content: {
        [e.ZH_CN]: "您关注的{{symbol}}{{timeType}}：{{threshold}}，24H涨跌幅{{percentChange24h}}，突破时间{{updateTime}}",
        [e.ZH_TW]: "您關註的{{symbol}}{{timeType}}：{{threshold}}，24H漲跌幅{{percentChange24h}}，突破時間{{updateTime}}",
        [e.EN]: "{{symbol}} {{timeType}}: {{threshold}}, 24H Change: {{percentChange24h}}. Triggered at: {{updateTime}}"
    }
});
u.set(-105, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{timeType}}：{{threshold}}",
        [e.ZH_TW]: "{{symbol}}{{timeType}}：{{threshold}}",
        [e.EN]: "{{symbol}} {{timeType}} at {{threshold}}"
    },
    content: {
        [e.ZH_CN]: "您关注的{{symbol}}{{timeType}}：{{threshold}}，24H涨跌幅{{percentChange24h}}，突破时间{{updateTime}}",
        [e.ZH_TW]: "您關註的{{symbol}}{{timeType}}：{{threshold}}，24H漲跌幅{{percentChange24h}}，突破時間{{updateTime}}",
        [e.EN]: "{{symbol}} {{timeType}}: {{threshold}}, 24H Change: {{percentChange24h}}. Triggered at: {{updateTime}}"
    }
});
u.set(106, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{timeType}}达到{{change}}",
        [e.ZH_TW]: "{{symbol}}{{timeType}}達到{{change}}",
        [e.EN]: "{{symbol}} {{timeType}} Reached {{change}}"
    },
    content: {
        [e.ZH_CN]: "您关注的{{symbol}}现报{{price}}，{{timeType}}{{change}}，突破时间 {{updateTime}}",
        [e.ZH_TW]: "您關注的{{symbol}}現報{{price}}，{{timeType}}{{change}}，突破時間 {{updateTime}}",
        [e.EN]: "{{symbol}} is now trading at {{price}}. {{timeType}}: {{change}} Breakout Time: {{updateTime}}"
    }
});
u.set(-106, {
    title: {
        [e.ZH_CN]: "{{symbol}}{{timeType}}达到{{change}}",
        [e.ZH_TW]: "{{symbol}}{{timeType}}達到{{change}}",
        [e.EN]: "{{symbol}} {{timeType}} Reached {{change}}"
    },
    content: {
        [e.ZH_CN]: "您关注的{{symbol}}现报{{price}}，{{timeType}}{{change}}，跌破时间 {{updateTime}}",
        [e.ZH_TW]: "您關注的{{symbol}}現報{{price}}，{{timeType}}{{change}}，跌破時間 {{updateTime}}",
        [e.EN]: '{{symbol}} is now trading at {{price}}. {{timeType}}: {{change}} Breakout Time: {{updateTime}}"'
    }
});
u.set(108, {
    title: {
        [e.ZH_CN]: "{{symbol}} {{fundsMovementType}}{{tradeType}}资金异动，请重点关注",
        [e.ZH_TW]: "{{symbol}} {{fundsMovementType}}{{tradeType}}資金異動，請重點關註",
        [e.EN]: "{{symbol}} {{tradeType}} Funds Shift ({{fundsMovementType}}): High Alert!"
    },
    content: {
        [e.ZH_CN]: "{{symbol}} {{fundsMovementType}}出现大量{{tradeType}}资金异常流入，现报{{price}}，24H涨跌幅{{percentChange24h}}，请注意市场行情变化。",
        [e.ZH_TW]: "{{symbol}} {{fundsMovementType}}出現大量{{tradeType}}資金異常流入，現報{{price}}，24H涨跌幅{{percentChange24h}}，請註意市場行情變化。",
        [e.EN]: "Significant unusual inflow detected in {{symbol}} {{tradeType}} funds {{fundsMovementType}}. now reported {{price}}, 24H Change: {{percentChange24h}}, Monitor market conditions closely."
    }
});
u.set(109, {
    title: {
        [e.ZH_CN]: "{{title}}",
        [e.ZH_TW]: "{{title}}",
        [e.EN]: "{{title}}"
    },
    content: {
        [e.ZH_CN]: "{{content}}",
        [e.ZH_TW]: "{{content}}",
        [e.EN]: "{{content}}"
    }
});
u.set(110, {
    title: {
        [e.ZH_CN]: "{{symbol}} {{tradeType}}资金活跃异常，可能是利多信号，请重点跟踪",
        [e.ZH_TW]: "{{symbol}} {{tradeType}}資金活躍異常，可能是利多信號，請重點跟蹤",
        [e.EN]: "{{symbol}} {{tradeType}} Capital Activity Surges – Potential Bullish Signal, Monitor Closely"
    },
    content: {
        [e.ZH_CN]: "{{symbol}} {{tradeType}}资金持续流入，24H涨跌幅{{percentChange24h}}，现报{{price}}，可能出现上涨行情，但需注意风险。",
        [e.ZH_TW]: "{{symbol}} {{tradeType}}資金持續流入，24H漲跌幅{{percentChange24h}}，現報{{price}}，可能出現上漲行情，但需註意風險。",
        [e.EN]: "{{symbol}} {{tradeType}} have seen continuous capital inflows, with a 24H increase of {{percentChange24h}}, currently trading at {{price}}. This may indicate an upward trend, but caution is advised."
    }
});
u.set(111, {
    title: {
        [e.ZH_CN]: "{{symbol}} 主力资金已出逃，资金异动实时追踪结束",
        [e.ZH_TW]: "{{symbol}} 主力資金已出逃，資金異動實時追蹤結束",
        [e.EN]: "{{symbol}} Whale Capital Exodus - Monitoring Concluded"
    },
    content: {
        [e.ZH_CN]: "{{symbol}} 疑似主力资金已出逃，资金异动监控结束，现报{{price}}，24H涨跌幅{{percentChange24h}}，注意市场风险。",
        [e.ZH_TW]: "{{symbol}} 疑似主力資金已出逃，資金異動監控結束，現報{{price}}，24H漲跌幅{{percentChange24h}}，注意市場風險。",
        [e.EN]: "Suspected whale capital outflow detected in {{symbol}}. Anomaly monitoring concluded. now reported {{price}}, 24H Change: {{percentChange24h}}. Exercise caution amid ongoing market risks."
    }
});
u.set(112, {
    title: {
        [e.ZH_CN]: "{{symbol}} FOMO情绪加剧，注意止盈，防范突发风险",
        [e.ZH_TW]: "{{symbol}} FOMO情緒加劇，注意止盈，防範突發風險",
        [e.EN]: "{{symbol}} FOMO Intensifies – Take Profits and Guard Against Sudden Risks"
    },
    content: {
        [e.ZH_CN]: "{{symbol}} 现报{{price}}，24H涨跌幅{{percentChange24h}}，注意风险管控。",
        [e.ZH_TW]: "{{symbol}} 現報{{price}}，24H漲跌幅{{percentChange24h}}，注意風險管控。",
        [e.EN]: "{{symbol}} is currently priced at {{price}}, 24H Change: {{percentChange24h}}. Risk management is advised."
    }
});
u.set(113, {
    title: {
        [e.ZH_CN]: "{{symbol}} 交易量激增，市场FOMO情绪，请注意关注",
        [e.ZH_TW]: "{{symbol}} 交易量激增，市場FOMO情緒，請注意關注",
        [e.EN]: "{{symbol}} Volume Surge - FOMO Alert"
    },
    content: {
        [e.ZH_CN]: "{{symbol}} 现报{{price}}，最近5分钟涨跌幅{{fiveMinPriceChange}}，{{tradeAmount24HContent}}涨跌幅{{percentChange24h}}，注意风险管控。",
        [e.ZH_TW]: "{{symbol}} 现报{{price}}，最近5分钟涨跌幅{{fiveMinPriceChange}}，{{tradeAmount24HContent}}涨跌幅{{percentChange24h}}，注意风险管控。",
        [e.EN]: "{{symbol}} is now {{price}}, {{fiveMinPriceChange}} in 5  minutes, {{tradeAmount24HContent}}24H Change: {{percentChange24h}}.Risk Caution Advised."
    }
});
u.set(114, {
    title: {
        [e.ZH_CN]: "{{symbol}} 追踪后的涨幅超过{{gains}}，移动止盈以保护利润",
        [e.ZH_TW]: "{{symbol}} 追蹤後的漲幅超過{{gains}}，移動止盈以保護利潤",
        [e.EN]: "{{symbol}} tracking increase of more than {{gains}}, move the stop profit to protect profits"
    },
    content: {
        [e.ZH_CN]: "AI追踪后涨幅{{gains}}，现报{{price}}，注意移动止盈以保护利润。",
        [e.ZH_TW]: "AI追蹤後漲幅{{gains}}，現報{{price}}，留意移動止盈以保護利潤。",
        [e.EN]: "AI tracking increase of {{gains}}, the current price is {{price}}, pay attention to move the stop profit to protect profits."
    }
});
const ne = {
    class: "warn-signal-message"
}
  , le = I({
    __name: "WarnSignalMessage",
    props: {
        data: {},
        ableToDetail: {
            type: Boolean,
            default: !0
        }
    },
    emits: ["toDetail", "toHash", "toAnnouncement"],
    setup(T, {emit: r}) {
        const t = T
          , N = r
          , _ = $()
          , g = R( () => _.language);
        async function f() {
            t.ableToDetail && N("toDetail", t.data.keyword)
        }
        async function Z() {
            N("toAnnouncement", t.data.id)
        }
        const w = new Map([[C.GAINS_FIXED, a("message.priceRiseTo")], [C.DECLINE_FIXED, a("message.priceFallTo")], [C.GAINS_MINUTE_5, a("message.gain5Min")], [C.DECLINE_MINUTE_5, a("message.decline5Min")], [C.GAINS_DAY_1, a("message.gain1Day")], [C.DECLINE_DAY_1, a("message.decline1Day")], [C.GAINS_DAY_7, a("message.gain7Day")], [C.DECLINE_DAY_7, a("message.decline7Day")]])
          , i = new Map([[1, a("common.spot")], [2, a("common.futures")]]);
        a("common.netInflow"),
        a("common.volume");
        function d() {
            if (!u.has(t.data.messageType))
                return s("div", null, null);
            const o = new W(u.get(t.data.messageType).title[g.value]);
            return o.setStrategy("symbol", () => s("span", {
                class: t.ableToDetail ? "color-primary cursor-pointer" : "",
                onClick: f
            }, [t.data.symbol])),
            o.setStrategy("timeType", () => w.get(t.data.timeType)),
            o.setStrategy("tradeType", () => i.get(t.data.tradeType)),
            o.setStrategy("threshold", () => s("span", {
                class: "color-primary"
            }, [n("$"), H(t.data.threshold).toPrice()])),
            o.setStrategy("change", () => {
                const y = Math.abs(Number(Number(t.data.change).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("total", () => t.data.inflowType === "INFLOW" ? `$${H(t.data.maxInflow).toPrice()}` : t.data.inflowType === "VOLUME" ? `$${H(t.data.maxAmount).toPrice()}` : "{{total}}"),
            o.setStrategy("value", () => `$${H(t.data.price * t.data.amount).toPrice()}`),
            o.setStrategy("address", () => A(t.data.address, 8, 4)),
            o.setStrategy("fundsMovementType", () => {
                if (t.data.fundsMovementType === 1)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "24H内";
                    case e.ZH_TW:
                        return "24H內";
                    case e.EN:
                        return "24H"
                    }
                else if (t.data.fundsMovementType === 2)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "24H外";
                    case e.ZH_TW:
                        return "24H外";
                    case e.EN:
                        return "Outside 24H"
                    }
                else
                    return t.data.fundsMovementType === 3 ? "" : "{{fundsMovementType}}"
            }
            ),
            o.setStrategy("title", () => {
                const y = ( () => {
                    switch (g.value) {
                    case e.ZH_CN:
                        return t.data.titleSimplified;
                    case e.ZH_TW:
                        return t.data.titleTraditional;
                    case e.EN:
                        return t.data.titleEnglish
                    }
                }
                )();
                return s("span", {
                    class: "hover:color-primary cursor-pointer",
                    onClick: Z
                }, [y])
            }
            ),
            o.setStrategy("gains", () => {
                const y = Math.abs(Number(Number(t.data.extField.gains).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("decline", () => {
                const y = Math.abs(Number(Number(t.data.extField.decline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.parser()
        }
        function L() {
            if (!u.has(t.data.messageType))
                return s("div", null, null);
            const o = new W(u.get(t.data.messageType).content[g.value]);
            return o.setStrategy("symbol", () => t.data.symbol),
            o.setStrategy("price", () => s("span", {
                class: "color-primary"
            }, [n("$"), H(t.data.price).toPrice()])),
            o.setStrategy("threshold", () => s("span", {
                class: "color-primary"
            }, [n("$"), H(t.data.threshold).toPrice()])),
            o.setStrategy("timeType", () => w.get(t.data.timeType)),
            o.setStrategy("tradeType", () => i.get(t.data.tradeType)),
            o.setStrategy("change", () => {
                const y = Math.abs(Number(Number(t.data.change).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("percentChange24h", () => {
                const y = Number(Number(t.data.percentChange24h).toFixed(2));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("total", () => t.data.inflowType === "INFLOW" ? `$${H(t.data.maxInflow).toPrice()}` : t.data.inflowType === "VOLUME" ? `$${H(t.data.maxAmount).toPrice()}` : "{{total}}"),
            o.setStrategy("times", () => t.data.times.map(y => y.replace(/(\D+)(\d+)/g, (E, k, G) => `${G}${k}`)).join(" ")),
            o.setStrategy("amount", () => H(t.data.amount).toFormatKMB(2)),
            o.setStrategy("value", () => `$${H(t.data.price * t.data.amount).toPrice()}`),
            o.setStrategy("flow", () => {
                if (t.data.flow === 1)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "向";
                    case e.ZH_TW:
                        return "向";
                    case e.EN:
                        return "to"
                    }
                else if (t.data.flow === 2)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "从";
                    case e.ZH_TW:
                        return "從";
                    case e.EN:
                        return "from"
                    }
                else
                    return "{{flow}}"
            }
            ),
            o.setStrategy("action", () => {
                if (t.data.flow === 1)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "转出";
                    case e.ZH_TW:
                        return "轉出"
                    }
                else if (t.data.flow === 2)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "收到";
                    case e.ZH_TW:
                        return "收到"
                    }
                else
                    return "{{action}}"
            }
            ),
            o.setStrategy("fromAddress", () => A(t.data.fromAddress, 8, 4)),
            o.setStrategy("toAddress", () => A(t.data.toAddress, 8, 4)),
            o.setStrategy("tradeHash", () => A(t.data.tradeHash, 8, 4)),
            o.setStrategy("updateTime", () => Y(t.data.updateTime).format("YYYY-MM-DD HH:mm:ss")),
            o.setStrategy("fundsMovementType", () => {
                if (t.data.fundsMovementType === 1)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "24H内";
                    case e.ZH_TW:
                        return "24H內";
                    case e.EN:
                        return "24H"
                    }
                else if (t.data.fundsMovementType === 2)
                    switch (g.value) {
                    case e.ZH_CN:
                        return "24H外";
                    case e.ZH_TW:
                        return "24H外";
                    case e.EN:
                        return "Outside 24H"
                    }
                else
                    return t.data.fundsMovementType === 3 ? "" : "{{fundsMovementType}}"
            }
            ),
            o.setStrategy("content", () => ""),
            o.setStrategy("fiveMinPriceChange", () => {
                const y = Number(Number(t.data.extField.fiveMinPriceChange).toFixed(2));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("tradeAmount24HContent", () => {
                var k;
                const y = ((k = t.data.extField) == null ? void 0 : k.tradeAmount24H) || void 0;
                if (!y)
                    return "";
                const E = H(y).toFormatKMB(2);
                switch (g.value) {
                case e.ZH_CN:
                    return s("span", null, [n("24H交易量"), s("span", {
                        class: "text-nowrap"
                    }, [E]), n("，")]);
                case e.ZH_TW:
                    return s("span", null, [n("24H交易量"), s("span", {
                        class: "text-nowrap"
                    }, [E]), n("，")]);
                case e.EN:
                    return s("span", null, [n("24H Vol: "), s("span", {
                        class: "text-nowrap"
                    }, [E]), n(", ")])
                }
            }
            ),
            o.setStrategy("gains", () => {
                const y = Math.abs(Number(Number(t.data.extField.gains).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.setStrategy("decline", () => {
                const y = Math.abs(Number(Number(t.data.extField.decline).toFixed(2)));
                return s("span", {
                    class: "text-nowrap"
                }, [y, n("%")])
            }
            ),
            o.parser()
        }
        return (o, y) => (p(),
        m("div", ne, [s(d, {
            class: "title"
        }), s(L, {
            class: "content"
        })]))
    }
})
  , Ne = M(le, [["__scopeId", "data-v-57379380"]])
  , ie = {
    key: 0,
    class: "tag tag-primary"
}
  , ce = {
    key: 1,
    class: "tag tag-inside"
}
  , ye = {
    key: 2,
    class: "tag tag-outside"
}
  , pe = {
    key: 0,
    class: "tag tag-success"
}
  , de = {
    key: 1,
    class: "tag tag-success"
}
  , me = {
    key: 2,
    class: "tag tag-bad"
}
  , ue = {
    key: 3,
    class: "tag tag-bad"
}
  , ge = {
    key: 4,
    class: "tag tag-fomo"
}
  , Se = {
    key: 5,
    class: "tag tag-success"
}
  , he = I({
    __name: "WarnSignalMessageTags",
    props: {
        data: {},
        showBullish: {
            type: Boolean,
            default: !0
        },
        observe: {
            type: Boolean,
            default: !1
        },
        messageType: {}
    },
    setup(T) {
        const r = T;
        return (t, N) => (p(),
        B(oe, {
            data: r.data,
            "show-score": !1,
            "show-risk-level": !1,
            observe: r.observe,
            messageType: r.messageType
        }, {
            predictType: P( () => [r.data.messageType === 109 ? (p(),
            m("div", ie, h(r.data.source), 1)) : b("", !0), r.data.fundsMovementType === 1 ? (p(),
            m("div", ce, h(S(a)("common.Inside24H")), 1)) : r.data.fundsMovementType === 2 ? (p(),
            m("div", ye, h(S(a)("common.Outside24H")), 1)) : b("", !0)]),
            other: P( () => [r.data.messageType === 110 ? (p(),
            m("div", pe, h(S(a)("layout.activeCapital")), 1)) : b("", !0), r.data.messageType === 110 && r.showBullish ? (p(),
            m("div", de, h(S(a)("layout.bullish")), 1)) : b("", !0), r.data.messageType === 111 ? (p(),
            m("div", me, h(S(a)("layout.message.QUIT_CHANCE")), 1)) : b("", !0), r.data.messageType === 112 ? (p(),
            m("div", ue, h(S(a)("layout.message.RISING_FOMO")), 1)) : b("", !0), r.data.messageType === 113 ? (p(),
            m("div", ge, " FOMO ")) : b("", !0), r.data.messageType === 114 ? (p(),
            m("div", Se, h(S(a)("layout.message.GAINS")), 1)) : b("", !0)]),
            _: 1
        }, 8, ["data", "observe", "messageType"]))
    }
})
  , fe = M(he, [["__scopeId", "data-v-9f23eafc"]]);
export {Ce as W, oe as a, Ne as b, fe as c, K as g, c as o};
