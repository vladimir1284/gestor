function plotChart(selector, labels, series, colors, total) {
  let cardColor, headingColor, axisColor, shadeColor, borderColor;

  cardColor = config.colors.white;
  headingColor = config.colors.headingColor;
  axisColor = config.colors.axisColor;
  borderColor = config.colors.borderColor;

  const chartStatistics = document.querySelector(selector),
    chartConfig = {
      chart: {
        height: 185,
        width: 185,
        type: "donut",
      },
      labels: labels,
      series: series,
      colors: colors,
      stroke: {
        width: 7,
        colors: cardColor,
      },
      dataLabels: {
        enabled: false,
        formatter: function (val, opt) {
          return parseInt(val) + "%";
        },
      },
      legend: {
        show: false,
      },
      grid: {
        padding: {
          top: 0,
          bottom: 0,
          right: 15,
        },
      },
      plotOptions: {
        pie: {
          donut: {
            size: "75%",
            labels: {
              show: true,
              value: {
                fontSize: "1.5rem",
                fontFamily: "Public Sans",
                color: headingColor,
                offsetY: -15,
                formatter: function (val) {
                  return "$" + parseInt(val);
                },
              },
              name: {
                offsetY: 20,
                fontFamily: "Public Sans",
              },
              total: {
                show: true,
                fontSize: "0.8125rem",
                color: axisColor,
                label: "Total",
                formatter: function (w) {
                  return total;
                },
              },
            },
          },
        },
      },
    };
  if (typeof chartStatistics !== undefined && chartStatistics !== null) {
    const statisticsChart = new ApexCharts(chartStatistics, chartConfig);
    statisticsChart.render();
  }
}
