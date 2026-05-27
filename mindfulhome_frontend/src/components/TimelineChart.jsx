import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';
import Icon from './Icon';
import { AlertTriangle, TrendingUp, MapPin, ChevronDown } from 'lucide-react';
import '../styles/timeline.css';

const TimelineChart = ({
    timelineData = [],
    events = [],
    scenario1 = null,
    scenario2 = null,
    showComparison = false
}) => {
    const [timeRange, setTimeRange] = useState('5years');
    const [showEvents, setShowEvents] = useState(true);

    const timeRangeOptions = [
        { value: '6months', label: '6 meses', months: 6 },
        { value: '1year', label: '1 año', months: 12 },
        { value: '5years', label: '5 años', months: 60 },
        { value: '10years', label: '10 años', months: 120 },
        { value: '15years', label: '15 años', months: 180 },
        { value: '20years', label: '20 años', months: 240 },
        { value: '25years', label: '25 años', months: 300 },
        { value: '30years', label: '30 años', months: 360 }
    ];

    const filteredData = useMemo(() => {
        const selectedOption = timeRangeOptions.find(opt => opt.value === timeRange);
        const maxMonths = selectedOption?.months || 60;

        const filterData = (data) => {
            if (!data || !Array.isArray(data)) return [];
            return data.filter(point => point.month <= maxMonths);
        };

        if (showComparison && scenario1 && scenario2) {
            const data1 = filterData(scenario1.timeline || timelineData);
            const data2 = filterData(scenario2.timeline || timelineData);

            const merged = [];
            const maxMonth = Math.max(
                data1[data1.length - 1]?.month || 0,
                data2[data2.length - 1]?.month || 0
            );

            for (let month = 0; month <= maxMonth; month++) {
                const point1 = data1.find(p => p.month === month);
                const point2 = data2.find(p => p.month === month);

                if (point1 || point2) {
                    merged.push({
                        month,
                        [`${scenario1.name}_liquidity`]: point1?.liquidity?.p50 || point1?.liquidity || null,
                        [`${scenario1.name}_stability`]: point1?.stability_probability || null,
                        [`${scenario1.name}_housing`]: point1?.housing_ratio?.p50 || point1?.housing_ratio || null,
                        [`${scenario2.name}_liquidity`]: point2?.liquidity?.p50 || point2?.liquidity || null,
                        [`${scenario2.name}_stability`]: point2?.stability_probability || null,
                        [`${scenario2.name}_housing`]: point2?.housing_ratio?.p50 || point2?.housing_ratio || null,
                    });
                }
            }
            return merged;
        }

        return filterData(timelineData);
    }, [timelineData, timeRange, timeRangeOptions, showComparison, scenario1, scenario2]);

    const filteredEvents = useMemo(() => {
        const selectedOption = timeRangeOptions.find(opt => opt.value === timeRange);
        const maxMonths = selectedOption?.months || 60;
        return events.filter(event => event.month <= maxMonths);
    }, [events, timeRange, timeRangeOptions]);

    const formatValue = (value, metric) => {
        if (value === null || value === undefined) return 'N/A';
        if (metric === 'liquidity') {
            return new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        }
        if (metric === 'stability' || metric === 'housing') {
            return `${Math.round(value * 100)}%`;
        }
        return value.toFixed(2);
    };

    const getMetricColor = (metric) => {
        const colors = {
            liquidity: '#467599',
            stability: '#7ADE5D',
            housing: '#77BABA'
        };
        return colors[metric] || '#999';
    };

    const getMetricName = (metric) => {
        const names = {
            liquidity: 'Liquidez',
            stability: 'Estabilidad',
            housing: 'Carga de vivienda'
        };
        return names[metric] || metric;
    };

    // Obtener ícono del evento según su tipo
    const getEventIcon = (type) => {
        switch(type) {
            case 'critical':
                return <AlertTriangle size={14} color="#ff6b6b" />;
            case 'recovery':
                return <TrendingUp size={14} color="#7ADE5D" />;
            default:
                return <MapPin size={14} color="#ffc107" />;
        }
    };

    const renderLines = () => {
        const lines = [];

        if (showComparison && scenario1 && scenario2) {
            const metrics = ['liquidity', 'stability', 'housing'];
            
            metrics.forEach(metric => {
                lines.push(
                    <Line
                        key={`${scenario1.name}_${metric}`}
                        type="monotone"
                        dataKey={`${scenario1.name}_${metric}`}
                        name={`${scenario1.name} - ${getMetricName(metric)}`}
                        stroke={getMetricColor(metric)}
                        strokeWidth={2}
                        dot={false}
                        connectNulls
                    />
                );
                
                lines.push(
                    <Line
                        key={`${scenario2.name}_${metric}`}
                        type="monotone"
                        dataKey={`${scenario2.name}_${metric}`}
                        name={`${scenario2.name} - ${getMetricName(metric)}`}
                        stroke={getMetricColor(metric)}
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        connectNulls
                    />
                );
            });
        } else {
            lines.push(
                <Line
                    key="liquidity"
                    type="monotone"
                    dataKey="liquidity.p50"
                    name="Liquidez (mediana)"
                    stroke={getMetricColor('liquidity')}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6 }}
                    connectNulls
                />
            );
            
            lines.push(
                <Line
                    key="stability"
                    type="monotone"
                    dataKey="stability_probability"
                    name="Probabilidad de estabilidad"
                    stroke={getMetricColor('stability')}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6 }}
                    connectNulls
                />
            );
            
            lines.push(
                <Line
                    key="housing"
                    type="monotone"
                    dataKey="housing_ratio.p50"
                    name="Housing ratio"
                    stroke={getMetricColor('housing')}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6 }}
                    connectNulls
                />
            );
        }

        return lines;
    };

    // Custom tooltip que también muestra información del evento si existe
    const CustomTooltip = ({ active, payload, label }) => {
        if (!active || !payload || !payload.length) return null;

        // Buscar si hay un evento en este mes
        const eventAtMonth = filteredEvents.find(event => event.month === label);
        const eventType = eventAtMonth?.type || null;

        return (
            <div className="timeline-tooltip">
                <div className="tooltip-header">
                    <strong>Mes {label}</strong>
                    {label % 12 === 0 && label > 0 && (
                        <span className="tooltip-year">(Año {label / 12})</span>
                    )}
                </div>
                
                {/* Mostrar información del evento si existe */}
                {eventAtMonth && (
                    <div className={`tooltip-event tooltip-event-${eventAtMonth.type}`}>
                        <div className="tooltip-event-icon">
                            {getEventIcon(eventAtMonth.type)}
                        </div>
                        <div className="tooltip-event-content">
                            <div className="tooltip-event-title">{eventAtMonth.title}</div>
                            <div className="tooltip-event-description">{eventAtMonth.description}</div>
                        </div>
                    </div>
                )}
                
                <div className="tooltip-body">
                    {payload.map((entry, index) => (
                        <div key={index} className="tooltip-item">
                            <span
                                className="tooltip-color"
                                style={{ backgroundColor: entry.color }}
                            />
                            <span className="tooltip-name">{entry.name}:</span>
                            <span className="tooltip-value">
                                {formatValue(entry.value, entry.dataKey?.includes('liquidity') ? 'liquidity' :
                                    entry.dataKey?.includes('stability') ? 'stability' : 'housing')}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="timeline-container">
            <div className="timeline-header">
                <div className="timeline-controls-left">
                    <Icon name="Calendar" size={16} color="#666" padding={0}/>
                    <div className="timeline-select-wrapper">
                        <select
                            className="timeline-select"
                            value={timeRange}
                            onChange={(e) => setTimeRange(e.target.value)}
                        >
                            {timeRangeOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="select-icon" size={16} />
                    </div>
                </div>

                <div className="timeline-controls-right">
                    <button
                        className={`event-chip ${showEvents ? 'active' : ''}`}
                        onClick={() => setShowEvents(!showEvents)}
                    >
                        <Icon name="Flag" size={14} color={showEvents ? '#467599' : '#999'}  backgroundColor='transparent' padding={2}/>
                        Mostrar eventos
                    </button>
                </div>
            </div>

            <div className="timeline-chart">
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart
                        data={filteredData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis
                            dataKey="month"
                            label={{ value: 'Mes', position: 'bottom', offset: 0 }}
                            tickFormatter={(value) => {
                                if (value === 0) return '0';
                                if (value % 12 === 0) return `${value / 12}a`;
                                return value % 6 === 0 ? value : '';
                            }}
                            interval="preserveStartEnd"
                        />
                        <YAxis
                            yAxisId="left"
                            label={{ value: showComparison ? 'Valor' : 'Monto/Probabilidad', angle: -90, position: 'insideLeft' }}
                            tickFormatter={(value) => {
                                if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(0)}M`;
                                if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(0)}k`;
                                if (value <= 1 && value >= 0) return `${Math.round(value * 100)}%`;
                                return value;
                            }}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            verticalAlign="top"
                            height={30}
                            wrapperStyle={{ paddingBottom: 10 }}
                        />

                        {renderLines()}

                        {/* Mostrar marcadores de eventos */}
                        {showEvents && filteredEvents.map((event, index) => {
                            const dataPoint = filteredData.find(d => d.month === event.month);
                            if (!dataPoint) return null;

                            let yValue = dataPoint.liquidity?.p50;
                            if (yValue === null || yValue === undefined) return null;

                            return (
                                <ReferenceDot
                                    key={`event-${index}`}
                                    x={event.month}
                                    y={yValue}
                                    r={8}
                                    fill={event.type === 'critical' ? '#ff6b6b' : event.type === 'recovery' ? '#7ADE5D' : '#ffc107'}
                                    stroke="#fff"
                                    strokeWidth={2}
                                    cursor="pointer"
                                />
                            );
                        })}
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Stats resumen */}
            <div className="timeline-stats">
                <div className="stat-card">
                    <div className="stat-label">Máximo de liquidez</div>
                    <div className="stat-value">
                        {formatValue(
                            Math.max(...filteredData.map(d => d.liquidity?.p50 || 0)),
                            'liquidity'
                        )}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Mejor estabilidad</div>
                    <div className="stat-value">
                        {formatValue(
                            Math.max(...filteredData.map(d => d.stability_probability || 0)),
                            'stability'
                        )}
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">Housing ratio promedio</div>
                    <div className="stat-value">
                        {formatValue(
                            filteredData.reduce((acc, d) => acc + (d.housing_ratio?.p50 || 0), 0) / (filteredData.length || 1),
                            'housing'
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TimelineChart;