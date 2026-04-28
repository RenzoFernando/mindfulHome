import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const DonutChart = ({ data, title, centerLabel }) => {
    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            return (
                <div className="chart-tooltip">
                    <p className="tooltip-label">{payload[0].name}</p>
                    <p className="tooltip-value">{payload[0].value}</p>
                </div>
            );
        }
        return null;
    };

    const renderCenterLabel = () => {
        if (centerLabel) {
            return (
                <text
                    x="50%"
                    y="45%"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="chart-center-label"
                >
                    {centerLabel}
                </text>
            );
        }
        return null;
    };

    return (
        <div className="donut-chart-container">
            {title && <h3 className="chart-title">{title}</h3>}
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={120}
                        outerRadius={170}
                        fill="#8884d8"
                        paddingAngle={2}
                        dataKey="value"
                        nameKey="name"
                        labelLine={false}
                    >
                        {data.map((entry, index) => (
                            <Cell 
                                key={`cell-${index}`} 
                                fill={entry.color}
                                stroke="white"
                                strokeWidth={0}
                            />
                        ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                    <Legend 
                        verticalAlign="bottom" 
                        align="center"
                        layout="horizontal"
                        iconType="circle"
                        wrapperStyle={{ paddingTop: "20px" }}
                    />
                    {renderCenterLabel()}
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default DonutChart;