from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from pyecharts.charts import Bar, Line, Grid, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from modules.history.models import Record
from .forms import DateRangeForm
import pandas as pd


class SleepAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        today = timezone.now().date()

        preset = self.request.GET.get('preset')
        if preset == 'week':
            start_date = today - timezone.timedelta(days=7)
        elif preset == 'month':
            start_date = today - timezone.timedelta(days=30)
        elif preset == 'year':
            start_date = today - timezone.timedelta(days=365)
        else:
            start_date = today - timezone.timedelta(days=7)

        end_date = today

        if preset:
            form = DateRangeForm(initial={
                'start_date': start_date,
                'end_date': end_date
            })
        else:
            form = DateRangeForm(self.request.GET or {
                'start_date': start_date,
                'end_date': end_date
            })

        context['form'] = form

        if form.is_valid() and not preset:
            start_date = form.cleaned_data.get('start_date') or start_date
            end_date = form.cleaned_data.get('end_date') or end_date

        records = Record.objects.filter(
            user=user,
            sleep_start__date__range=(start_date, end_date)
        )

        context.update({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'period_info': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
            'records_count': records.count(),
            'no_data': not records.exists()
        })

        if not records.exists():
            return context

        desired_hours = 8
        df = pd.DataFrame(list(records.values('sleep_start', 'sleep_end')))
        df['sleep_start'] = pd.to_datetime(df['sleep_start'])
        df['sleep_end'] = pd.to_datetime(df['sleep_end'])

        df['duration'] = (df['sleep_end'] - df['sleep_start']).dt.total_seconds()
        df['date'] = df['sleep_end'].dt.strftime('%d.%m')
        df['bedtime'] = df['sleep_start'].dt.hour + df['sleep_start'].dt.minute / 60
        df['wakeup'] = df['sleep_end'].dt.hour + df['sleep_end'].dt.minute / 60 + 3
        df['deficit'] = (df['duration'] < desired_hours * 3600)

        deficit_days = df['deficit'].sum()
        total_days = len(df)
        normal_days = total_days - deficit_days

        context['duration_chart'] = self.create_duration_chart(df)
        context['wakeup_chart'] = self.create_time_chart(df, 'wakeup', 'Время пробуждения')
        context['avg_duration'] = self.format_duration(df['duration'].mean())
        context['deficit_chart'] = self.create_deficit_chart(deficit_days, normal_days)

        return context

    def create_duration_chart(self, df):
        bar = (
            Bar(init_opts=opts.InitOpts(
                theme=ThemeType.WALDEN,
                width="100%",
                height="450px"
            ))
            .add_xaxis(df['date'].tolist())
            .add_yaxis(
                "Часы сна",
                (df['duration'] / 3600).round(1).tolist(),
                itemstyle_opts=opts.ItemStyleOpts(color='#5470C6'))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Продолжительность сна", pos_top="20px"),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode(
                        "function (params) {"
                        "  return params.name + ': ' + params.value[1].toFixed(1) + ' ч';"
                        "}"
                    )
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        formatter=JsCode("function(value) {return value.toFixed(1) + ' ч';}")
                    ),
                    splitline_opts=opts.SplitLineOpts(is_show=True)
                )
            )
        )

        grid = (
            Grid()
            .add(bar, grid_opts=opts.GridOpts(
                pos_bottom="15%",
                pos_top="20%"
            ))
        )

        return grid.render_embed()

    def create_time_chart(self, df, field, title):
        line = (
            Line(init_opts=opts.InitOpts(
                theme=ThemeType.WALDEN,
                width="100%",
                height="450px"
            ))
            .add_xaxis(df['date'].tolist())
            .add_yaxis(
                title,
                df[field].round(1).tolist(),
                is_smooth=True,
                symbol="circle",
                symbol_size=8,
                linestyle_opts=opts.LineStyleOpts(width=2))
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    pos_top="20px",
                ),
                tooltip_opts=opts.TooltipOpts(
                    formatter=JsCode(
                        "function (params) {"
                        "  return params.name + ': ' + params.value[1].toFixed(1) + ' ч';"
                        "}"
                    )
                ),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        margin=30
                    ),
                    boundary_gap=True
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        formatter=JsCode("function(value) {return value.toFixed(1) + ' ч';}")
                    ),
                    min_=2,
                    max_=14,
                    interval=1,
                    splitline_opts=opts.SplitLineOpts(is_show=True)
                )
            )
        )

        grid = (
            Grid()
            .add(line, grid_opts=opts.GridOpts(
                pos_bottom="15%",
                pos_top="20%"
            ))
        )

        return grid.render_embed()

    def create_deficit_chart(self, deficit_days, normal_days):
        deficit_days = int(deficit_days)
        normal_days = int(normal_days)

        if deficit_days + normal_days == 0:
            return "<div class='no-data'>Нет данных для отображения</div>"

        pie = (
            Pie(init_opts=opts.InitOpts(
                theme=ThemeType.WALDEN,
                width="100%",
                height="450px",
                bg_color="rgba(255, 255, 255, 0.0)"
            ))
            .add(
                series_name="Сон",
                data_pair=[
                    ("Дни с недосыпом", deficit_days),
                    ("Дни с нормой", normal_days),
                ],
                radius=["35%", "60%"],
                center=["50%", "55%"],
                label_opts=opts.LabelOpts(
                    position="outside",
                    formatter="{b|{b}:} {d}%",
                    rich={
                        "b": {"fontSize": 12, "lineHeight": 20}
                    }
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Соответствие норме сна",
                    pos_top="10px",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(
                        font_size=18,
                        color="#2c3e50"
                    )
                ),
                legend_opts=opts.LegendOpts(
                    orient="vertical",
                    pos_top="60px",
                    pos_left="10px",
                    item_width=14,
                    item_height=14,
                    textstyle_opts=opts.TextStyleOpts(
                        font_size=12
                    )
                ),
                tooltip_opts=opts.TooltipOpts(
                    formatter="{b}: {c} дней ({d}%)"
                )
            )
            .set_series_opts(
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width=2,
                    border_color="#fff"
                )
            )
        )

        return pie.render_embed()

    def format_duration(self, seconds):
        if pd.isna(seconds):
            return "Нет данных"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} ч {minutes} мин"
