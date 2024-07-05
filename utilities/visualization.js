const data = [
    {category: 'A', value: 30},
    {category: 'B', value: 80},
    {category: 'C', value: 45},
    {category: 'D', value: 60},
    {category: 'E', value: 20},
    {category: 'F', value: 90},
    {category: 'G', value: 50},
];

const svg = d3.select('body').append('svg')
    .attr('width', 500)
    .attr('height', 300);

svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', (d, i) => i * 70)
    .attr('y', (d) => 300 - d.value)
    .attr('width', 65)
    .attr('height', (d) => d.value)
    .attr('fill', 'steelblue');
