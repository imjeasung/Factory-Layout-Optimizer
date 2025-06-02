# 🏭 Factory Layout Optimizer | 공장 레이아웃 최적화 시스템

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-orange.svg)](https://matplotlib.org/)

> **English** | [한국어](#korean-section)

## 🎯 Overview

An AI-powered factory layout optimization system using Genetic Algorithm (GA) to maximize production efficiency while minimizing material flow distances. This system intelligently arranges manufacturing equipment to achieve optimal production throughput and workflow efficiency.

### Key Features
- **Genetic Algorithm Optimization**: Advanced evolutionary computation for layout optimization
- **Multi-objective Optimization**: Balances production throughput and material flow distance
- **Real-time Visualization**: Interactive layout visualization with matplotlib
- **Constraint Handling**: Considers equipment footprint, clearance, and spatial constraints
- **Progress Monitoring**: Real-time optimization progress tracking
- **Flexible Configuration**: Customizable equipment definitions and process sequences

## 🚀 Quick Start

### Prerequisites
```bash
pip install matplotlib
```

### Installation & Usage
```bash
git clone https://github.com/yourusername/Smart-Factory-Layout-Optimizer.git
cd Smart-Factory-Layout-Optimizer
python GA_Facility_Optimizer.py
```

## 🛠 Technical Specifications

### Algorithm Parameters
- **Population Size**: 300 individuals per generation
- **Generations**: 300 iterations
- **Mutation Rate**: 0.5 (50%)
- **Crossover Rate**: 0.8 (80%)
- **Elite Preservation**: Top 5 individuals per generation

### Optimization Objectives
1. **Maximize Throughput**: Target production rate optimization
2. **Minimize Distance**: Reduce material flow distances between equipment
3. **Constraint Satisfaction**: Ensure spatial and operational constraints

## 📊 Output & Visualization

The system generates:
- **Layout Visualization**: Color-coded equipment placement with clearance zones
- **Performance Graphs**: Fitness evolution, distance optimization, throughput analysis
- **Statistical Reports**: Generation-wise performance metrics

### Sample Output Files
- `ga_optimized_layout_visualization.png`: Final optimized layout
- `ga_factory_layout_analysis_plots.png`: Performance analysis charts

## 🔧 Customization

### Equipment Configuration
```python
machines_definitions = [
    {"id": 0, "name": "원자재_투입", "footprint": (2, 2), "cycle_time": 20, "clearance": 1},
    {"id": 1, "name": "1차_절삭", "footprint": (3, 3), "cycle_time": 35, "clearance": 1},
    # Add more equipment definitions...
]
```

### Factory Dimensions
```python
FACTORY_WIDTH = 28
FACTORY_HEIGHT = 28
```

## 📈 Performance Metrics

- **Fitness Function**: Weighted combination of throughput and distance
- **Production Target**: 35 units per hour (configurable)
- **Material Speed**: 0.5 units per second (configurable)

---

## Korean Section

# 🏭 공장 레이아웃 최적화 시스템

## 🎯 프로젝트 개요

유전 알고리즘을 활용하여 공장 레이아웃을 최적화하는 AI 시스템입니다. 생산 효율성을 극대화하면서 물류 동선을 최소화하여 최적의 설비 배치를 찾아줍니다.

### 주요 기능
- **유전 알고리즘 최적화**: 진화 연산을 통한 레이아웃 최적화
- **다중 목표 최적화**: 생산량과 이동 거리를 동시에 고려
- **실시간 시각화**: matplotlib을 활용한 대화형 레이아웃 시각화
- **제약 조건 처리**: 설비 크기, 클리어런스, 공간 제약 고려
- **진행 상황 모니터링**: 실시간 최적화 진행 상황 추적
- **유연한 설정**: 설비 정의 및 공정 순서 커스터마이징 가능

## 🛠 기술 사양

### 알고리즘 매개변수
- **집단 크기**: 세대당 300개 개체
- **세대 수**: 300회 반복
- **변이율**: 0.5 (50%)
- **교차율**: 0.8 (80%)
- **엘리트 보존**: 세대당 상위 5개 개체

### 최적화 목표
1. **생산량 최대화**: 목표 생산율 최적화
2. **거리 최소화**: 설비 간 물류 이동 거리 단축
3. **제약 조건 만족**: 공간 및 운영 제약 조건 준수

## 📊 결과 및 시각화

시스템 출력 결과:
- **레이아웃 시각화**: 클리어런스 영역을 포함한 색상별 설비 배치도
- **성능 그래프**: 적합도 진화, 거리 최적화, 생산량 분석
- **통계 보고서**: 세대별 성능 지표

### 출력 파일
- `ga_optimized_layout_visualization.png`: 최종 최적화된 레이아웃
- `ga_factory_layout_analysis_plots.png`: 성능 분석 차트

## 🚀 사용법

### 환경 설정
```bash
pip install matplotlib
```

### 실행 방법
```bash
git clone https://github.com/yourusername/Smart-Factory-Layout-Optimizer.git
cd Smart-Factory-Layout-Optimizer
python GA_Facility_Optimizer.py
```

## 🔧 커스터마이징

### 설비 설정
```python
machines_definitions = [
    {"id": 0, "name": "원자재_투입", "footprint": (2, 2), "cycle_time": 20, "clearance": 1},
    {"id": 1, "name": "1차_절삭", "footprint": (3, 3), "cycle_time": 35, "clearance": 1},
    # 추가 설비 정의...
]
```

## 📈 성능 지표

- **적합도 함수**: 생산량과 거리의 가중 조합
- **생산 목표**: 시간당 35개 (설정 가능)
- **물료 이동 속도**: 초당 0.5 단위 (설정 가능)

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created with ❤️ [imjeasung]
