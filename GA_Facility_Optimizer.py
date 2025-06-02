import random
import math
import copy
# import numpy as np # 필요시 사용
import os
import signal
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
interrupted = False

# --- 기존 유틸리티 함수들 (PPO 코드에서 가져옴) ---
class Machine:
    def __init__(self, id, name, footprint, cycle_time=0, clearance=0, wall_affinity=False):
        self.id = id; self.name = name; self.footprint = footprint; self.cycle_time = cycle_time
        self.clearance = clearance; self.wall_affinity = wall_affinity; self.position = None

# 머신 정의
machines_definitions = [
    # 기존 16개 설비 (일부 클리어런스 조정 가능)
    {"id": 0, "name": "원자재_투입", "footprint": (2, 2), "cycle_time": 20, "clearance": 1},
    {"id": 1, "name": "1차_절삭", "footprint": (3, 3), "cycle_time": 35, "clearance": 1},
    {"id": 2, "name": "밀링_가공", "footprint": (4, 2), "cycle_time": 45, "clearance": 1},
    {"id": 3, "name": "드릴링", "footprint": (2, 2), "cycle_time": 25, "clearance": 1},
    {"id": 4, "name": "열처리_A", "footprint": (3, 4), "cycle_time": 70, "clearance": 2},
    {"id": 5, "name": "정밀_가공_A", "footprint": (3, 2), "cycle_time": 40, "clearance": 1},
    {"id": 6, "name": "조립_A", "footprint": (2, 3), "cycle_time": 55, "clearance": 2},
    {"id": 7, "name": "최종_검사_A", "footprint": (1, 2), "cycle_time": 15, "clearance": 1},
    {"id": 8, "name": "2차_절삭", "footprint": (3, 2), "cycle_time": 30, "clearance": 1},
    {"id": 9, "name": "표면_처리", "footprint": (2, 4), "cycle_time": 50, "clearance": 2},
    {"id": 10, "name": "세척_공정_1", "footprint": (2, 2), "cycle_time": 20, "clearance": 1},
    {"id": 11, "name": "열처리_B", "footprint": (4, 4), "cycle_time": 75, "clearance": 2},
    {"id": 12, "name": "정밀_가공_B", "footprint": (2, 3), "cycle_time": 42, "clearance": 1},
    {"id": 13, "name": "부품_조립", "footprint": (3, 3), "cycle_time": 60, "clearance": 1},
    {"id": 14, "name": "품질_검사_B", "footprint": (2, 1), "cycle_time": 18, "clearance": 1},
    {"id": 15, "name": "포장_라인_A", "footprint": (4, 3), "cycle_time": 30, "clearance": 2},
    # 신규 14개 설비 추가
    # {"id": 16, "name": "용접_스테이션", "footprint": (3, 4), "cycle_time": 65, "clearance": 2},
    # {"id": 17, "name": "도장_부스", "footprint": (4, 3), "cycle_time": 80, "clearance": 2},
    # {"id": 18, "name": "건조로", "footprint": (2, 5), "cycle_time": 90, "clearance": 1}, # 긴 설비
    # {"id": 19, "name": "CNC_선반", "footprint": (3, 2), "cycle_time": 50, "clearance": 1},
    # {"id": 20, "name": "레이저_커팅기", "footprint": (4, 3), "cycle_time": 55, "clearance": 2},
    # {"id": 21, "name": "프레스_기계", "footprint": (3, 3), "cycle_time": 40, "clearance": 1},
    # {"id": 22, "name": "반제품_보관소", "footprint": (5, 4), "cycle_time": 10, "clearance": 1}, # 큰 면적, 짧은 시간
    # {"id": 23, "name": "자동화_검사대", "footprint": (2, 2), "cycle_time": 22, "clearance": 1},
    # {"id": 24, "name": "조립_B", "footprint": (3, 2), "cycle_time": 58, "clearance": 1},
    # {"id": 25, "name": "세척_공정_2", "footprint": (2, 2), "cycle_time": 20, "clearance": 1},
    # {"id": 26, "name": "최종_검사_C", "footprint": (1, 2), "cycle_time": 16, "clearance": 1},
    # {"id": 27, "name": "특수_가공기", "footprint": (2, 4), "cycle_time": 70, "clearance": 2},
    # {"id": 28, "name": "포장_라인_B", "footprint": (4, 3), "cycle_time": 32, "clearance": 2},
    # {"id": 29, "name": "출하_대기존", "footprint": (5, 3), "cycle_time": 5, "clearance": 1}  # 큰 면적, 매우 짧은 시간
]

# 공정 시퀀스 정의
all_machine_ids_for_sequence = list(range(len(machines_definitions)))
random.shuffle(all_machine_ids_for_sequence)
PROCESS_SEQUENCE = all_machine_ids_for_sequence
# print(f"사용될 공정 시퀀스: {PROCESS_SEQUENCE}")

# 프로세스 스퀀스를 지정하고 싶으면 위 랜덤 주석처리 -> 아래 시퀀스 주석 해제 -> 이후 원하는 스퀀스로 수정
# PROCESS_SEQUENCE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # 선형 16단계 공정

# 팩토리 크기 정의(설비의 개수에 따라 변경 가능)
FACTORY_WIDTH = 28
FACTORY_HEIGHT = 28

# 목표 생산량 및 시간 상수
TARGET_PRODUCTION_PER_HOUR = 35
SECONDS_PER_HOUR = 3600
MATERIAL_TRAVEL_SPEED_UNITS_PER_SECOND = 0.5


def initialize_layout_grid(width, height):
    return [[-1 for _ in range(height)] for _ in range(width)]

def can_place_machine(grid, machine_footprint, machine_clearance, x, y, factory_w, factory_h):
    m_width, m_height = machine_footprint
    if not (0 <= x and x + m_width <= factory_w and 0 <= y and y + m_height <= factory_h):
        return False
    check_x_start = x - machine_clearance
    check_x_end = x + m_width + machine_clearance
    check_y_start = y - machine_clearance
    check_y_end = y + m_height + machine_clearance
    for i in range(max(0, check_x_start), min(factory_w, check_x_end)):
        for j in range(max(0, check_y_start), min(factory_h, check_y_end)):
            is_machine_body = (x <= i < x + m_width) and (y <= j < y + m_height)
            if grid[i][j] != -1:
                if is_machine_body:
                    return False
                elif machine_clearance > 0:
                    return False
    return True

def place_machine_on_grid(grid, machine_id, machine_footprint, x, y):
    m_width, m_height = machine_footprint
    for i in range(x, x + m_width):
        for j in range(y, y + m_height):
            grid[i][j] = machine_id

def calculate_total_distance(machine_positions, process_sequence):
    total_distance = 0
    if not machine_positions or len(process_sequence) < 2:
        return float('inf')
    for m_id in process_sequence:
        if m_id not in machine_positions or 'center_x' not in machine_positions[m_id] or 'center_y' not in machine_positions[m_id]:
            return float('inf')
    for i in range(len(process_sequence) - 1):
        m1_id, m2_id = process_sequence[i], process_sequence[i+1]
        if m1_id not in machine_positions or m2_id not in machine_positions:
             return float('inf')
        pos1_center_x = machine_positions[m1_id]['center_x']
        pos1_center_y = machine_positions[m1_id]['center_y']
        pos2_center_x = machine_positions[m2_id]['center_x']
        pos2_center_y = machine_positions[m2_id]['center_y']
        distance = math.sqrt((pos1_center_x - pos2_center_x)**2 + (pos1_center_y - pos2_center_y)**2)
        total_distance += distance
    return total_distance

def get_machine_cycle_time(machine_id, all_machines_data):
    for m_def in all_machines_data:
        if m_def["id"] == machine_id:
            return m_def["cycle_time"]
    return float('inf')

def estimate_line_throughput(machine_positions, process_sequence, all_machines_data, travel_speed):
    if not machine_positions or not process_sequence: return 0.0
    for m_id in process_sequence:
        if m_id not in machine_positions or 'center_x' not in machine_positions[m_id] or 'center_y' not in machine_positions[m_id]:
            return 0.0
    max_stage_time = 0.0
    for i in range(len(process_sequence)):
        current_machine_id = process_sequence[i]
        machine_cycle_time = get_machine_cycle_time(current_machine_id, all_machines_data)
        if machine_cycle_time == float('inf'): return 0.0
        travel_time = 0.0
        if i > 0:
            prev_machine_id = process_sequence[i-1]
            if prev_machine_id in machine_positions and current_machine_id in machine_positions:
                pos_prev, pos_curr = machine_positions[prev_machine_id], machine_positions[current_machine_id]
                distance = math.sqrt((pos_prev['center_x'] - pos_curr['center_x'])**2 + (pos_prev['center_y'] - pos_curr['center_y'])**2)
                if travel_speed > 0: travel_time = distance / travel_speed
                else: travel_time = float('inf')
            else: return 0.0
        current_stage_total_time = machine_cycle_time + travel_time
        if current_stage_total_time > max_stage_time: max_stage_time = current_stage_total_time
    if max_stage_time <= 0 or max_stage_time == float('inf'): return 0.0
    return SECONDS_PER_HOUR / max_stage_time

def print_layout(grid, machine_positions):
    print("--- 현재 레이아웃 ---")
    transposed_grid = [list(row) for row in zip(*grid)]
    for row_idx_actual in range(FACTORY_HEIGHT -1, -1, -1):
        row_to_print = [f"{grid[col_idx_actual][row_idx_actual]:2d}" if grid[col_idx_actual][row_idx_actual] != -1 else "__" for col_idx_actual in range(FACTORY_WIDTH)]
        print(f"Y{row_idx_actual:<2}| " + " ".join(row_to_print))
    header = "    " + " ".join(f"X{i:<2}" for i in range(FACTORY_WIDTH))
    print("-" * len(header)); print(header)
    if not machine_positions: print("배치된 설비 없음"); return
    print("\n--- 설비 위치 (좌상단, 중심) ---")
    for machine_id in PROCESS_SEQUENCE:
        if machine_id in machine_positions:
            pos_data = machine_positions[machine_id]
            machine_def = next((m for m in machines_definitions if m["id"] == machine_id), None)
            machine_name = machine_def["name"] if machine_def else "알수없음"
            print(f"설비 ID {machine_id} ({machine_name}): 좌상단 ({pos_data['x']}, {pos_data['y']}), 중심 ({pos_data['center_x']:.1f}, {pos_data['center_y']:.1f})")

def visualize_layout_plt(grid_layout_to_show, machine_positions_map, factory_w, factory_h, process_sequence_list, machine_definitions_list, filename="ga_best_layout.png"):
    """
    matplotlib을 사용하여 최종 레이아웃을 시각화하고 파일로 저장합니다.
    """
    fig, ax = plt.subplots(1, figsize=(factory_w/2, factory_h/2 + 1)) # 그림 크기 조절
    ax.set_xlim(-0.5, factory_w - 0.5)
    ax.set_ylim(-0.5, factory_h - 0.5)
    ax.set_xticks(range(factory_w))
    ax.set_yticks(range(factory_h))
    ax.set_xticklabels(range(factory_w))
    ax.set_yticklabels(range(factory_h))
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis() # 화면 위쪽을 Y=0으로 (일반적인 배열 인덱스와 유사하게)

    # 색상맵 (머신 ID별로 다른 색상) - 수정된 부분
    cmap = plt.colormaps.get_cmap('viridis')
    num_machines = len(machine_definitions_list)
    
    # PROCESS_SEQUENCE 순서대로 머신 정보 가져오기 위한 딕셔너리
    machines_dict_by_id = {m['id']: m for m in machine_definitions_list}

    for machine_id_in_seq in process_sequence_list:
        if machine_id_in_seq in machine_positions_map:
            pos_data = machine_positions_map[machine_id_in_seq]
            machine_info = machines_dict_by_id.get(machine_id_in_seq)

            if machine_info:
                x, y = pos_data['x'], pos_data['y']
                width, height = machine_info['footprint']
                clearance = machine_info.get('clearance', 0)
                
                # 머신 본체 그리기 - 수정된 색상 사용 방법
                color_value = machine_id_in_seq / max(num_machines - 1, 1)  # 0~1 사이의 값으로 정규화
                rect_body = patches.Rectangle((x - 0.5, y - 0.5), width, height,
                                              linewidth=1.5, edgecolor='black',
                                              facecolor=cmap(color_value), alpha=0.7)
                ax.add_patch(rect_body)

                # 머신 ID 및 이름 텍스트 (중앙에 표시)
                # 글자 크기, 위치 등은 필요에 따라 조절
                text_x = x + width / 2 - 0.5
                text_y = y + height / 2 - 0.5
                ax.text(text_x, text_y, f"M{machine_id_in_seq}\n({machine_info['name'][:5]}..)",
                        ha='center', va='center', fontsize=6, color='white', weight='bold')
                
                # 클리어런스 영역 그리기 (선택적) - 수정된 색상 사용 방법
                if clearance > 0:
                    rect_clearance = patches.Rectangle(
                        (x - clearance - 0.5, y - clearance - 0.5),
                        width + 2 * clearance, height + 2 * clearance,
                        linewidth=1, edgecolor=cmap(color_value),
                        facecolor='none', linestyle=':', alpha=0.5
                    )
                    ax.add_patch(rect_clearance)

    plt.title("Optimized Factory Layout (GA)")
    plt.xlabel("Factory Width (X)")
    plt.ylabel("Factory Height (Y)")
    plt.gca().invert_yaxis() # Y축을 위에서 아래로 증가하도록 (일반적인 그리드처럼)

    try:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 최종 레이아웃 시각화 이미지 저장 완료: {filename}")
    except Exception as e:
        print(f"레이아웃 이미지 저장 중 오류 발생: {e}")
    plt.close(fig) # 다음 플롯을 위해 그림 닫기


def signal_handler(signum, frame):
    global interrupted
    print("\n\n⚠️  CTRL+C 감지! 현재 세대 완료 후 그래프를 저장하고 종료합니다...")
    interrupted = True

# --- GA 하이퍼파라미터 ---
POPULATION_SIZE = 300       # 한 세대 내 개체(염색체 또는 해)의 총 수. 클수록 다양한 해를 탐색하지만 계산량이 증가합니다.
NUM_GENERATIONS = 300     # 알고리즘이 반복할 총 세대 수. 충분히 커야 최적해에 수렴할 가능성이 높아집니다.
MUTATION_RATE = 0.5     # 각 개체가 변이 연산을 겪을 확률 (0.0 ~ 1.0). 너무 낮으면 지역 최적해에 빠지기 쉽고, 너무 높으면 수렴이 불안정해질 수 있습니다.
CROSSOVER_RATE = 0.8      # 두 부모 개체 간에 교차 연산이 발생할 확률 (0.0 ~ 1.0). 일반적으로 높은 값을 사용합니다.
ELITISM_COUNT = 5         # 각 세대에서 다음 세대로 직접 전달될 가장 우수한 개체의 수. 최고 해의 손실을 방지합니다.
TOURNAMENT_SIZE = 5       # 토너먼트 선택 방식에서 각 토너먼트에 참여할 개체의 수. 클수록 선택 압력이 높아져 우수한 개체가 더 잘 선택됩니다.

# 적합도 함수 가중치 (문제의 특성 및 목표에 따라 실험적으로 조정 필요)
FITNESS_THROUGHPUT_WEIGHT = 1.0       # 적합도 계산 시 생산량에 적용될 가중치.
FITNESS_DISTANCE_WEIGHT = 0.005     # 적합도 계산 시 총 이동 거리에 적용될 가중치. 거리는 최소화 대상이므로 음수 또는 빼기 형태로 반영됩니다. (값의 스케일에 따라 조정)
BONUS_FOR_TARGET_ACHIEVEMENT_FACTOR = 0.2 # 시간당 목표 생산량 달성 시 적합도에 추가될 보너스의 비율 (생산량 * 이 값).

# --- GA 핵심 함수 ---
def create_individual(machines_in_processing_order_defs, factory_w, factory_h):
    chromosome = []
    grid = initialize_layout_grid(factory_w, factory_h)
    for machine_def in machines_in_processing_order_defs:
        valid_placements = []
        m_footprint, m_clearance = machine_def["footprint"], machine_def.get("clearance", 0)
        for x in range(factory_w - m_footprint[0] + 1):
            for y in range(factory_h - m_footprint[1] + 1):
                if can_place_machine(grid, m_footprint, m_clearance, x, y, factory_w, factory_h):
                    valid_placements.append((x, y))
        if not valid_placements: chromosome.append((-1, -1))
        else:
            chosen_x, chosen_y = random.choice(valid_placements)
            chromosome.append((chosen_x, chosen_y))
            place_machine_on_grid(grid, machine_def["id"], m_footprint, chosen_x, chosen_y)
    return chromosome

# [MODIFIED] calculate_fitness 함수 수정: 거리, 생산량, 유효성 여부 반환
def calculate_fitness(chromosome, machines_defs_ordered_by_proc_seq, process_seq_ids,
                      factory_w, factory_h, target_prod_throughput, material_travel_speed):
    grid = initialize_layout_grid(factory_w, factory_h)
    machine_positions = {}
    all_machines_placed_successfully = True
    
    # 기본 반환값 (유효하지 않을 경우)
    result = {"fitness": -float('inf'), "distance": float('inf'), "throughput": 0.0, "is_valid": False}

    if len(chromosome) != len(machines_defs_ordered_by_proc_seq):
        return result

    for i, machine_def in enumerate(machines_defs_ordered_by_proc_seq):
        pos_x, pos_y = chromosome[i]
        if pos_x == -1 and pos_y == -1:
            all_machines_placed_successfully = False; break
        m_footprint, m_clearance, m_id = machine_def["footprint"], machine_def.get("clearance", 0), machine_def["id"]
        if not can_place_machine(grid, m_footprint, m_clearance, pos_x, pos_y, factory_w, factory_h):
            all_machines_placed_successfully = False; break
        place_machine_on_grid(grid, m_id, m_footprint, pos_x, pos_y)
        machine_positions[m_id] = {"x": pos_x, "y": pos_y, "center_x": pos_x + m_footprint[0]/2.0, "center_y": pos_y + m_footprint[1]/2.0}

    if not all_machines_placed_successfully or len(machine_positions) != len(machines_defs_ordered_by_proc_seq):
        return result # 기본 유효하지 않음 결과 반환

    total_dist = calculate_total_distance(machine_positions, process_seq_ids)
    throughput = estimate_line_throughput(machine_positions, process_seq_ids, machines_definitions, material_travel_speed)

    if total_dist == float('inf') or throughput == 0.0: # 계산 오류 시 유효하지 않음 처리
        return result

    fitness_val = (FITNESS_THROUGHPUT_WEIGHT * throughput) - (FITNESS_DISTANCE_WEIGHT * total_dist)
    if throughput >= target_prod_throughput: fitness_val += throughput * BONUS_FOR_TARGET_ACHIEVEMENT_FACTOR
    
    result["fitness"] = fitness_val
    result["distance"] = total_dist
    result["throughput"] = throughput
    result["is_valid"] = True
    return result

def selection(population_with_eval_results, tournament_size): # 입력 변경
    if not population_with_eval_results: return None
    actual_tournament_size = min(tournament_size, len(population_with_eval_results))
    if actual_tournament_size == 0: return None
    tournament = random.sample(population_with_eval_results, actual_tournament_size)
    winner = max(tournament, key=lambda item: item[1]['fitness']) # item[1] is a dict
    return winner[0] # Return chromosome

def crossover(parent1_chromo, parent2_chromo, crossover_rate):
    child1, child2 = list(parent1_chromo), list(parent2_chromo)
    if random.random() < crossover_rate:
        num_genes = len(parent1_chromo)
        if num_genes > 1:
            cut_point = random.randint(1, num_genes - 1)
            child1 = parent1_chromo[:cut_point] + parent2_chromo[cut_point:]
            child2 = parent2_chromo[:cut_point] + parent1_chromo[cut_point:]
    return child1, child2

def mutate(chromosome, machines_in_proc_order_defs, factory_w, factory_h, mutation_rate_per_gene=0.1):
    mutated_chromosome = list(chromosome)
    num_genes = len(chromosome)
    if num_genes == 0: return mutated_chromosome
    for i in range(num_genes):
        if random.random() < mutation_rate_per_gene:
            machine_def_to_mutate = machines_in_proc_order_defs[i]
            m_footprint, m_clearance = machine_def_to_mutate["footprint"], machine_def_to_mutate.get("clearance", 0)
            temp_grid = initialize_layout_grid(factory_w, factory_h)
            for k in range(num_genes):
                if k == i: continue
                prev_pos_x, prev_pos_y = mutated_chromosome[k]
                if prev_pos_x == -1 and prev_pos_y == -1: continue
                other_machine_def = machines_in_proc_order_defs[k]
                place_machine_on_grid(temp_grid, other_machine_def["id"], other_machine_def["footprint"], prev_pos_x, prev_pos_y)
            valid_new_placements = []
            for x_coord in range(factory_w - m_footprint[0] + 1):
                for y_coord in range(factory_h - m_footprint[1] + 1):
                    if can_place_machine(temp_grid, m_footprint, m_clearance, x_coord, y_coord, factory_w, factory_h):
                        valid_new_placements.append((x_coord,y_coord))
            if valid_new_placements: mutated_chromosome[i] = random.choice(valid_new_placements)
    return mutated_chromosome

# --- 메인 실행 블록 ---
if __name__ == '__main__':
    print("공장 레이아웃 최적화 (유전 알고리즘 버전) - 추가 분석 포함")
    signal.signal(signal.SIGINT, signal_handler)

    machines_for_ga_processing_order = [next(m for m in machines_definitions if m["id"] == pid) for pid in PROCESS_SEQUENCE]
    num_total_machines = len(machines_for_ga_processing_order)

    print(f"초기 집단 생성 중 (크기: {POPULATION_SIZE})...")
    population = [create_individual(machines_for_ga_processing_order, FACTORY_WIDTH, FACTORY_HEIGHT) for _ in range(POPULATION_SIZE)]
    print("초기 집단 생성 완료.")
    
    best_overall_fitness = -float('inf')
    best_overall_chromosome = None
    
    # [NEW] 로그 리스트 초기화
    generation_best_fitness_log = []
    generation_avg_fitness_log = []
    generation_best_distance_log = []      # 추가: 최고 개체 거리 로그
    generation_best_throughput_log = []    # 추가: 최고 개체 생산량 로그
    generation_valid_ratio_log = []        # 추가: 유효 개체 비율 로그

    for generation in range(1, NUM_GENERATIONS + 1):
        if interrupted:
            print(f"\n🛑 유전 알고리즘 중단 요청됨 (세대 {generation})")
            break

        all_eval_results = [] # (chromosome, eval_dict) 저장
        current_gen_total_fitness = 0
        current_gen_valid_individuals_count = 0

        for chromo in population:
            eval_dict = calculate_fitness(chromo, machines_for_ga_processing_order, PROCESS_SEQUENCE,
                                          FACTORY_WIDTH, FACTORY_HEIGHT, TARGET_PRODUCTION_PER_HOUR,
                                          MATERIAL_TRAVEL_SPEED_UNITS_PER_SECOND)
            all_eval_results.append((chromo, eval_dict))
            if eval_dict["is_valid"]:
                current_gen_total_fitness += eval_dict["fitness"]
                current_gen_valid_individuals_count += 1
        
        if not all_eval_results:
             print(f"세대 {generation}: 평가 결과 없음! 알고리즘 중단."); break

        # 현재 세대 최고 개체 정보
        current_gen_best_item = max(all_eval_results, key=lambda item: item[1]['fitness'])
        current_gen_best_chromosome = current_gen_best_item[0]
        current_gen_best_eval_dict = current_gen_best_item[1]
        
        current_gen_best_fitness = current_gen_best_eval_dict['fitness']
        current_gen_best_distance = current_gen_best_eval_dict['distance']
        current_gen_best_throughput = current_gen_best_eval_dict['throughput']
        
        generation_best_fitness_log.append(current_gen_best_fitness)
        generation_best_distance_log.append(current_gen_best_distance) # 유효하지 않으면 inf가 기록될 수 있음
        generation_best_throughput_log.append(current_gen_best_throughput) # 유효하지 않으면 0이 기록될 수 있음

        valid_ratio = (current_gen_valid_individuals_count / POPULATION_SIZE) * 100 if POPULATION_SIZE > 0 else 0
        generation_valid_ratio_log.append(valid_ratio)
        
        current_gen_avg_fitness = (current_gen_total_fitness / current_gen_valid_individuals_count) if current_gen_valid_individuals_count > 0 else -float('inf')
        generation_avg_fitness_log.append(current_gen_avg_fitness)

        if current_gen_best_fitness > best_overall_fitness:
            best_overall_fitness = current_gen_best_fitness
            best_overall_chromosome = current_gen_best_chromosome
            print(f"  🌟 세대 {generation}: 새 최고 적합도 발견! {best_overall_fitness:.2f} (거리: {current_gen_best_distance:.2f}, 생산량: {current_gen_best_throughput:.2f})")

        print(f"세대 {generation}/{NUM_GENERATIONS} - 최고F: {current_gen_best_fitness:.2f}, 평균F: {current_gen_avg_fitness:.2f}, 유효율: {valid_ratio:.1f}%")
        
        new_population = []
        # 엘리트주의
        all_eval_results.sort(key=lambda item: item[1]['fitness'], reverse=True)
        for i in range(ELITISM_COUNT):
            if i < len(all_eval_results) and all_eval_results[i][1]["is_valid"]:
                 new_population.append(all_eval_results[i][0])

        num_offspring_to_generate = POPULATION_SIZE - len(new_population)
        eligible_parents_for_selection = [item for item in all_eval_results if item[1]["is_valid"]]
        if not eligible_parents_for_selection: eligible_parents_for_selection = all_eval_results # 최악의 경우

        current_offspring_count = 0
        while current_offspring_count < num_offspring_to_generate:
            if not eligible_parents_for_selection: break
            parent1_chromo = selection(eligible_parents_for_selection, TOURNAMENT_SIZE)
            parent2_chromo = selection(eligible_parents_for_selection, TOURNAMENT_SIZE)
            if parent1_chromo is None or parent2_chromo is None: # 부모 선택에 문제가 생기면
                if eligible_parents_for_selection: # 유효한 부모 후보가 있다면 거기서 임의로 가져옴
                    parent1_chromo = random.choice(eligible_parents_for_selection)[0] if parent1_chromo is None else parent1_chromo
                    parent2_chromo = random.choice(eligible_parents_for_selection)[0] if parent2_chromo is None else parent2_chromo
                else: # 정말 아무것도 없으면 중단
                    print("경고: 더 이상 부모를 선택할 수 없습니다.")
                    break
            
            child1_chromo, child2_chromo = crossover(parent1_chromo, parent2_chromo, CROSSOVER_RATE)
            if random.random() < MUTATION_RATE: child1_chromo = mutate(child1_chromo, machines_for_ga_processing_order, FACTORY_WIDTH, FACTORY_HEIGHT, mutation_rate_per_gene=0.05)
            if random.random() < MUTATION_RATE: child2_chromo = mutate(child2_chromo, machines_for_ga_processing_order, FACTORY_WIDTH, FACTORY_HEIGHT, mutation_rate_per_gene=0.05)
            new_population.append(child1_chromo); current_offspring_count +=1
            if current_offspring_count < num_offspring_to_generate: new_population.append(child2_chromo); current_offspring_count +=1
        
        while len(new_population) < POPULATION_SIZE:
            # print(f"경고: 다음 세대 개체 수가 부족하여 무작위 개체 추가.")
            new_population.append(create_individual(machines_for_ga_processing_order, FACTORY_WIDTH, FACTORY_HEIGHT))
        population = new_population[:POPULATION_SIZE]

    # --- 최종 결과 출력 ---
    print("\n--- 최종 결과 (유전 알고리즘) ---")
    print(f"사용될 공정 시퀀스: {PROCESS_SEQUENCE}")
    if best_overall_chromosome:
        print(f"최고 적합도: {best_overall_fitness:.2f}")
        final_grid_layout = initialize_layout_grid(FACTORY_WIDTH, FACTORY_HEIGHT) # 시각화를 위해 그리드 필요
        final_machine_positions_map = {}
        # is_final_layout_valid = True # final_eval_dict_for_best["is_valid"]로 대체

        final_eval_dict_for_best = calculate_fitness(best_overall_chromosome, machines_for_ga_processing_order, PROCESS_SEQUENCE,
                                                     FACTORY_WIDTH, FACTORY_HEIGHT, TARGET_PRODUCTION_PER_HOUR,
                                                     MATERIAL_TRAVEL_SPEED_UNITS_PER_SECOND)

        if final_eval_dict_for_best["is_valid"]:
            # 머신 위치 및 그리드 구성 (print_layout 및 visualize_layout_plt를 위해)
            for i, machine_def_item in enumerate(machines_for_ga_processing_order):
                pos_x_final, pos_y_final = best_overall_chromosome[i]
                place_machine_on_grid(final_grid_layout, machine_def_item["id"], machine_def_item["footprint"], pos_x_final, pos_y_final)
                final_machine_positions_map[machine_def_item["id"]] = {
                    "x": pos_x_final, "y": pos_y_final,
                    "center_x": pos_x_final + machine_def_item["footprint"][0] / 2.0,
                    "center_y": pos_y_final + machine_def_item["footprint"][1] / 2.0,
                }
            
            # 1. 기존 텍스트 기반 레이아웃 출력
            print_layout(final_grid_layout, final_machine_positions_map)
            
            # 2. [NEW] Matplotlib을 사용한 레이아웃 시각화 및 저장
            layout_image_filename = 'ga_optimized_layout_visualization.png'
            if interrupted: # 전역 변수 interrupted 사용
                 layout_image_filename = 'ga_optimized_layout_visualization_interrupted.png'
            visualize_layout_plt(final_grid_layout, # 현재 그리드 자체는 visualize_layout_plt에서 직접 사용 안함
                                 final_machine_positions_map, 
                                 FACTORY_WIDTH, FACTORY_HEIGHT,
                                 PROCESS_SEQUENCE, # 시퀀스 정보 전달
                                 machines_definitions, # 전체 머신 정보 전달
                                 filename=layout_image_filename)

            print(f"해당 레이아웃의 총 이동 거리: {final_eval_dict_for_best['distance']:.2f}")
            print(f"해당 레이아웃의 시간당 생산량: {final_eval_dict_for_best['throughput']:.2f} (목표: {TARGET_PRODUCTION_PER_HOUR})")
        else:
            print("오류: 최종 최고 염색체가 유효하지 않은 레이아웃입니다.")
            if best_overall_chromosome: print("최고 염색체:", best_overall_chromosome)

    else: print("유효한 최적 레이아웃을 찾지 못했습니다.")

    # --- 그래프 생성 (matplotlib 필요) ---
    # 기존 적합도 그래프
    try:
        plt.figure(figsize=(12, 7))
        plt.subplot(2, 2, 1) # 2x2 그리드의 첫 번째 플롯
        plt.plot(generation_best_fitness_log, label='Best Fitness', color='blue')
        plt.plot(generation_avg_fitness_log, label='Average Fitness (Valid)', color='cyan', linestyle='--')
        plt.xlabel('Generation'); plt.ylabel('Fitness')
        plt.title('GA Fitness Progress'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)

        # [NEW] 최고 개체 이동 거리 그래프
        plt.subplot(2, 2, 2) # 2x2 그리드의 두 번째 플롯
        # inf 값을 가진 경우 plot에서 제외하거나 매우 큰 값으로 대체 (또는 y_lim 설정)
        plot_distances = [d if d != float('inf') else max(filter(lambda x: x!=float('inf'), generation_best_distance_log), default=0)*1.1 for d in generation_best_distance_log]
        if not any(d != float('inf') for d in generation_best_distance_log) and generation_best_distance_log: # 모든 값이 inf인 경우
            plot_distances = [0] * len(generation_best_distance_log) # 0으로 표시 또는 다른 처리

        plt.plot(plot_distances, label='Best Individual Distance', color='green')
        plt.xlabel('Generation'); plt.ylabel('Total Distance')
        plt.title('Best Individual Distance'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)
        if any(d == float('inf') for d in generation_best_distance_log): plt.text(0.05, 0.95, "Note: 'inf' distances capped for plotting", transform=plt.gca().transAxes, fontsize=8, verticalalignment='top')


        # [NEW] 최고 개체 생산량 그래프
        plt.subplot(2, 2, 3) # 2x2 그리드의 세 번째 플롯
        plt.plot(generation_best_throughput_log, label='Best Individual Throughput', color='red')
        plt.xlabel('Generation'); plt.ylabel('Throughput')
        plt.axhline(y=TARGET_PRODUCTION_PER_HOUR, color='gray', linestyle=':', label=f'Target TPH ({TARGET_PRODUCTION_PER_HOUR})')
        plt.title('Best Individual Throughput'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)

        # [NEW] 유효 개체 비율 그래프
        plt.subplot(2, 2, 4) # 2x2 그리드의 네 번째 플롯
        plt.plot(generation_valid_ratio_log, label='Valid Individuals Ratio (%)', color='purple')
        plt.xlabel('Generation'); plt.ylabel('Valid Ratio (%)'); plt.ylim(0, 100)
        plt.title('Valid Individuals Ratio'); plt.legend(); plt.grid(True, linestyle=':', alpha=0.7)
        
        plt.tight_layout() # 플롯 간 간격 자동 조절
        graph_filename_output = 'ga_factory_layout_analysis_plots.png'
        if interrupted: graph_filename_output = 'ga_factory_layout_analysis_plots_interrupted.png'
        plt.savefig(graph_filename_output, dpi=300)
        print(f"📊 분석 그래프 저장 완료: {graph_filename_output}")
        plt.close()
    except ImportError: print("matplotlib 라이브러리가 설치되어 있지 않아 그래프를 생성할 수 없습니다.")
    except Exception as e_graph: print(f"그래프 생성 중 예상치 못한 오류 발생: {e_graph}")
        
    if interrupted: print("\n✅ 안전하게 중단되었습니다.")
    print("\n프로그램 종료.")
