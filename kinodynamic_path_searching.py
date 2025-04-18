# -*- coding: utf-8 -*-


import numpy as np
import heapq
import matplotlib.pyplot as plt
import itertools
from scipy.linalg import expm
from scipy.integrate import quad_vec
import sympy as sp
from mpl_toolkits.mplot3d import Axes3D

class Node:
  def __init__(
        self,
        state = np.ndarray,
        parent = None,
        g = 0,
        h = 0,
        f = 0
    ):
        self.state = state
        self.parent = parent
        self.g = g
        self.h = h
        self.parent = parent
        self.f = self.g + self.h



  def node_printer(self):
      position = self.state[:3]
      velocity = self.state[3:]
      return f"Position: {position} Velocity: {velocity}"

  def __str__(self):
        return f"State: {self.state}, g: {self.g}, h: {self.h}, f: {self.f}"

  def __lt__(self, other):
    if self.f == other.f:
        return np.any(self.state < other.state)
    return self.f < other.f

# start_state = np.array([0,0,0,0,0,0])
# start_node = Node(start_state)

# goal_state = np.array([1,1,1,0,0,0])
# goal_node = Node(goal_state)

# print("start node:", start_node.node_printer())
# print("goal node:", goal_node.node_printer())

def initiallize():
  nodes = []
  start_state = np.array([0,0,0,0.01,0.01,0.01])
  start_node = Node(start_state)
  goal_state = np.array([4,3,5,0,0,0])
  goal_node = Node(goal_state)
  obstacle_state = np.array([5,5,5,0,0,0])
  obstacle_node = Node(obstacle_state)
  heapq.heappush(nodes, (start_node.g, start_node))
  print(nodes)
  return nodes, goal_node, obstacle_node

def expand(n_c, n_g):
  print("expanding this node", n_c)


  primitives = []
  u = [-2,-1,0,1,2]
  u_diff = [-1,-2,-1,-1,-2]
  if (np.linalg.norm(n_c.state[3:])) > 2:
    print("using different controls now")
    U_D = list(itertools.product(u_diff, repeat=3))
  else:
    U_D = list(itertools.product(u, repeat=3))


  if (np.linalg.norm(n_c.state[3:])) > 2.9:
    print("using this now 0.05",np.linalg.norm(n_c.state[3:]))
    tau = 0.05
  if (np.linalg.norm(n_c.state[3:])) > 3:
    print("using this now 0.09",np.linalg.norm(n_c.state[3:]))
    tau = 0.09
  if (np.linalg.norm(n_c.state[3:])) < 2.5:
     print("using the tau 0.4",np.linalg.norm(n_c.state[3:]))
     tau = 0.4
  if np.linalg.norm(n_c.state[:3] - n_g.state[:3]) < 0.5:
    print("using this now 0.05")
    tau = 0.05

  top = np.hstack((np.zeros((3,3)), np.eye(3)))
  bottom = np.hstack((np.zeros((3,3)), np.zeros((3,3))))
  A = np.vstack((top, bottom))
  B = np.zeros((6, 3))
  B[3:6, 0:3] = np.eye(3)
  e_At =  expm(A * tau)
  x_0 = n_c.state
  tf = tau
  # print("haha", Node)

  for u_d in U_D:
        u_d = np.array(u_d)
        def integrand(s):
           return expm(A * (tau - s)) @ B @ u_d
        result, _ = quad_vec(integrand, 0, tau)
        x_new = e_At @ x_0 + result
        primitives.append((x_new, u_d))


  return primitives

def prune(nodes):
  _,goal,_ = initiallize()
  pruned_nodes = []
  d_s = []
  for node in nodes:
    dist = np.linalg.norm(node[0][:3] - goal.state[:3])
    # print(dist)
    d_s.append([dist,node[0],node[1]])
  d_s.sort(key=lambda x: x[0])
  # print("d_n", d_s)
  s_n = [pair for pair in d_s]
  # print("s_n", s_n)
  sorted_nodes = [pair[1] for pair in d_s]
  # print("sorted_nodes", sorted_nodes)
  sorted_nodes_u_d = [pair[2] for pair in d_s]
  # print("sorted_nodes_u_d", sorted_nodes_u_d)
  for i in range(30):
    pruned_nodes.append([sorted_nodes[i], sorted_nodes_u_d[i]])

  # print("pruned_nodes", pruned_nodes)
  return pruned_nodes

def check_feasibility(node):
   v_max = 3.0
   u_max = 2.0
   states = node[0]
   u_d = node[1]
  #  print("u_d", u_d)
   v = states[3:]
  #  print("v",v)
   truth_teller = False
   v_norm = np.linalg.norm(v)
   u_norm = np.linalg.norm(u_d)
   if round(v_norm, 1) <= v_max and round(u_norm,1) <= u_max:
      truth_teller = True
   else:
      print("the trajectory is not feasible with velocity and acc as", round(v_norm, 1), u_norm)
      truth_teller = False
   return truth_teller

def edge_cost(node, pop_node):
  # print("nc", node[1])
  u_d = node[1]
  state = pop_node.state[3:]
  v = state
  u_norm = np.linalg.norm(u_d)
  p = 1
  if (np.linalg.norm(v)) > 2.9:
    tau = 0.05
  if (np.linalg.norm(v)) > 3:
    tau = 0.09
  if (np.linalg.norm(v)) < 2.5:
     tau = 0.4
  edge_cost = (u_norm + p)*tau
  # print("edge_cost", edge_cost)

  return edge_cost

def heuristic(nc, g_node):
  print("heuristics from current node", nc)
  # print("g_node", g_node)
  T = sp.symbols('T')
  nc_state = np.array(nc[:3])
  goal_state = np.array(g_node.state[:3])
  nc_vel = np.array(nc[3:])
  goal_vel = np.zeros(3) if np.all(goal_state[3:] == 0) else goal_state[3:]
  # print("nc_vel", nc_vel)
  # print("nc_state", nc_state)
  # print("goal_state", goal_state)
  # print("goal_vel", goal_vel)
  delta_pos = goal_state - nc_state
  delta_vel = goal_vel - nc_vel
  alpha = (-12 * (delta_pos - nc_vel * T) / T**3) + (6 * delta_vel / T**2)
  beta = (6 * (delta_pos - nc_vel * T) / T**2) - (2 * delta_vel / T)
  alpha = sp.simplify(alpha)
  beta = sp.simplify(beta)
  # print("alpha", alpha)
  # print("beta", beta)

  J_u = []

  for i, e in enumerate(alpha):
      j_u = (1/3)*sp.Pow(e,2)*(T**3) + (e*beta[i])*(T**2) + (beta[i]**2)*(T)
      j_u = sp.simplify(j_u)
      J_u.append(j_u)

  # print("J_u", J_u)

  J_star = np.sum(J_u)
  rho = 1
  J_star += rho*T
  # print("J_star", J_star)

  dj_dt = sp.diff(J_star, T)
  # print("dj_dt", dj_dt)

  solutions = sp.solveset(dj_dt, T, domain=sp.S.Reals)
  # print("solutions", solutions)

  T_opt = None
  for sol in solutions:
        if sol.is_real and sol > 0:
            T_opt = float(sol)
            break

  J_star_numeric = J_star.subs(T, T_opt)
  heuristic_cost = float(J_star_numeric)
  # print(J_star_numeric)

  return heuristic_cost

def compute_alpha_beta(T, delta_p, delta_v):
    if T <= 0:
        return 0, 0
    alpha = (-12 / T**3) * delta_p + (6 / T**2) * delta_v
    beta = (6 / T**2) * delta_p - (2 / T) * delta_v
    return alpha, beta

def check_trajectory_feasibility(state_c, state_g,obs,j_u,state_v,goal_v, T_opt, v_max=3.0, a_max=2.0, num_samples=100):
    alpha = np.zeros(3)
    beta = np.zeros(3)
    # print("state_c", state_c)
    # print("state_g", state_g)
    for mu in range(3):
        print("mu", mu)
        p_mu_c = state_c[mu]
        v_mu_c = state_v[mu]
        p_mu_g = state_g[mu]
        v_mu_g = goal_v[mu]
        delta_p = p_mu_g - p_mu_c - v_mu_c * T_opt
        delta_v = v_mu_g - v_mu_c
        alpha[mu], beta[mu] = compute_alpha_beta(T_opt, delta_p, delta_v)


    u_0 = beta
    u_0_norm = np.linalg.norm(u_0)
    if round(u_0_norm,1) > a_max:
        print(f"Trajectory infeasible at t=0: u_norm={u_0_norm}")
        return False


    u_T = alpha * T_opt + beta
    u_T_norm = np.linalg.norm(u_T)
    if round(u_T_norm,1) > a_max:
        print(f"Trajectory infeasible at t={T_opt}: u_norm={u_T_norm}")
        return False

    t_samples = np.linspace(0, T_opt, num_samples)


    for t in t_samples:
        v_t = np.zeros(3)
        for mu in range(3):
            v_t[mu] = (1/2) * alpha[mu] * t**2 + beta[mu] * t + state_v[mu]
        v_norm = np.linalg.norm(v_t)
        if v_norm > v_max:
            print(f"Trajectory infeasible at t={t}: v_norm={v_norm}")
            return False



    print("Trajectory is feasible")
    return True

def analytical_expand(nc, g_node,P,obs, v_max=3.0, a_max=2.0, rho=1.0):
  # print("nc", nc)
  # print("g_node", g_node)
  T = sp.symbols('T')
  nc_state = np.array(nc.state[:3])
  goal_state = np.array(g_node.state[:3])
  nc_vel = np.array(nc.state[3:])
  goal_vel = np.zeros(3) if np.all(goal_state[3:] == 0) else goal_state[3:]
  # print("nc_vel", nc_vel)
  # print("nc_state", nc_state)
  # print("goal_state", goal_state)
  # print("goal_vel", goal_vel)
  delta_pos = goal_state - nc_state
  delta_vel = goal_vel - nc_vel
  alpha = (-12 * (delta_pos - nc_vel * T) / T**3) + (6 * delta_vel / T**2)
  beta = (6 * (delta_pos - nc_vel * T) / T**2) - (2 * delta_vel / T)
  alpha = sp.simplify(alpha)
  beta = sp.simplify(beta)
  # print("alpha", alpha)
  # print("beta", beta)

  J_u = []

  for i, e in enumerate(alpha):
      j_u = (1/3)*sp.Pow(e,2)*(T**3) + (e*beta[i])*(T**2) + (beta[i]**2)*(T)
      j_u = sp.simplify(j_u)
      J_u.append(j_u)

  J_star = np.sum(J_u)
  J_star += rho*T
  # print("J_star", J_star)

  dj_dt = sp.diff(J_star, T)
  # print("dj_dt", dj_dt)

  solutions = sp.solveset(dj_dt, T, domain=sp.S.Reals)
  # print("solutions", solutions)

  T_opt = None
  for sol in solutions:
        if sol.is_real and sol > 0:
            T_opt = float(sol)
            break

  J_star_numeric = J_star.subs(T, T_opt)
  if not check_trajectory_feasibility(nc_state, goal_state,obs.state,j_u, nc_vel, goal_vel, T_opt, v_max, a_max):
        print("AnalyticExpand: Trajectory is not feasible")
        return False,None


  g_temp = nc.g + J_star_numeric
  goal_node = Node(state=goal_state, parent=nc, g=g_temp, h=0, f=g_temp)
  P.append((goal_node.f, goal_node))
  print("AnalyticExpand: Successfully connected to goal")

  trajectory = []
  t_vals = np.linspace(0, T_opt, 10)
  for t in t_vals:
    T_i = T_opt
    alpha = (-12 * (delta_pos - nc_vel * T_i) / T_i**3) + (6 * delta_vel / T_i**2)
    beta = (6 * (delta_pos - nc_vel * T_i) / T_i**2) - (2 * delta_vel / T_i)
    print("alpha", alpha)
    print("beta", beta)
    p_t = (1/6)*alpha*t**3 + (1/2)*beta*t**2 + nc_vel*t + nc_state
    print("these are the pt", p_t,t)
    trajectory.append(p_t)
  return True, trajectory

def ReachGoal(nc, goal_state, pos_tolerance=0.2):
    nc_pos = nc[:3]
    goal_pos = goal_state.state[:3]
    nc_vel = nc[3:]
    goal_vel = np.zeros(3) if np.all(goal_state.state[3:] == 0) else goal_state.state[3:]
    if np.linalg.norm(nc_vel) == np.linalg.norm(goal_vel):
        print("velocity is same as goal")
        return True
    pos_diff = np.linalg.norm(goal_pos - nc_pos)
    if pos_diff < pos_tolerance:
        print(f"Goal reached! Position difference: {pos_diff}")
        return True
    return False

def plot_3d_trajectory(visited_positions, edges, final_path, start_pos, goal_pos):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot visited nodes
    # visited_positions = np.array(visited_positions)
    # for i in visited_positions:
    #     ax.scatter(i[0], i[1], i[2], c='gray', marker='o', s=20, alpha=0.5,label='Visited Nodes')
    # ax.scatter(visited_positions[:, 0], visited_positions[:, 1], visited_positions[:, 2],
    #            c='gray', marker='o', s=20, alpha=0.5, label='Visited Nodes')

    # Plot edges (motion primitives)
    for edge in edges:
        parent_pos, child_pos = edge
        ax.plot([parent_pos[0], child_pos[0]],
                [parent_pos[1], child_pos[1]],
                [parent_pos[2], child_pos[2]],
                'r-', alpha=0.3)

    # Plot final path
    if final_path:
        final_path = np.array(final_path)
        for i in final_path:
            ax.scatter(i[0], i[1], i[2], c='b', marker='o', s=20)
        # ax.plot(final_path[:, 0], final_path[:, 1], final_path[:, 2],
        #         'b-', linewidth=2, label='Final Path')

    # Plot start and goal
    ax.scatter(start_pos[0], start_pos[1], start_pos[2], c='green', marker='*', s=200, label='Start')
    ax.scatter(goal_pos[0], goal_pos[1], goal_pos[2], c='red', marker='*', s=200, label='Goal')

    # Add obstacles (example: cuboids)
    def plot_cuboid(center, size, ax, color='blue', alpha=0.1):
        x, y, z = center
        dx, dy, dz = size
        xx = [x - dx/2, x + dx/2]
        yy = [y - dy/2, y + dy/2]
        zz = [z - dz/2, z + dz/2]
        for s, e in itertools.combinations(np.array(list(itertools.product(xx, yy, zz))), 2):
            if np.sum(np.abs(s - e)) == (xx[1] - xx[0]) or \
               np.sum(np.abs(s - e)) == (yy[1] - yy[0]) or \
               np.sum(np.abs(s - e)) == (zz[1] - zz[0]):
                ax.plot3D(*zip(s, e), color=color, alpha=alpha)

    obstacles = [
        ([3, 2, 1], [1, 1, 1]),  # (center, size)
        ([6, 3, 1], [1, 1, 1]),
        ([4, 1, 0.5], [1, 1, 1])
    ]
    for center, size in obstacles:
        plot_cuboid(center, size, ax)

    # Set labels and limits
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim(-1, 10)
    ax.set_ylim(-1, 10)
    ax.set_zlim(-1, 10)
    ax.legend()
    plt.title("3D Kinodynamic Path Search")
    plt.show()



P = []
P , g_node, obs = initiallize()
Visited = []
visited_positions = []
edges = []
final_path = []

while P != []:
  # print("Penut", P)
  pop = heapq.heappop(P)
  start = np.zeros(3) if np.all(pop[1].state[:3] == 0) else pop[1].state[:3]
  P.clear()
  print("here are the pop nodes", P)
  # print("pop_node", start)

  pop_node = pop[1]
  Visited.append(pop_node.state[:3])

  visited_positions.append(pop_node.state[:3])
  # print("pop_node", pop_node)



  if ReachGoal(pop_node.state, g_node) == True:
            current = pop_node
            print("reached")
            Visited.append(g_node.state[:3])
            g_node.parent = current
            edges.append((pop_node.state[:3], g_node.state[:3]))
            Visited.reverse()
            break


  nc_pos = pop_node.state[:3]
  goal_pos = g_node.state[:3]
  pos_diff = np.linalg.norm(nc_pos - goal_pos)
  # if pos_diff < 3:
  #        analytical,traj_points = analytical_expand(pop_node, g_node,P,obs)
  #        print("AnalyticExpand called")
  #        if analytical == True:
  #           print("Goal reached via AnalyticExpand!")
  #           current = g_node
  #           Visited.append(current.state[:3])
  #           analytical_traj_edges = [(traj_points[i], traj_points[i+1]) for i in range(len(traj_points)-1)]
  #           edges.extend(analytical_traj_edges)
  #           current.parent = pop_node
  #           Visited.reverse()
  #           break

  print("expanding here now")
  print(" --- ")
  print(" --- ")
  print(" --- ")
  primitives = expand(pop_node, g_node)
  pruned_nodes = prune(primitives)
  print("current state", pop_node.state[:3])
  for node in pruned_nodes:
    print("node", node)
    states = node[0]
    if np.array_equal(states[:3], Visited[-1]):
      print("skipped cuz same state")
      continue

    # if [states] not in Visited:
    if not any(np.array_equal(states, visited_state) for visited_state in Visited):
      if check_feasibility(node) == True:
        gtemp_ni = pop_node.g + edge_cost(node, pop_node)
        # node_nc = Node(states)
        # print("P", P)
        edges.append((pop_node.state[:3], states[:3]))

        if [(gtemp_ni, states)] not in P:
          ni = Node(states)
          ni.parent = pop_node
          ni.g = gtemp_ni
          total_cost = gtemp_ni + heuristic(states,g_node)
          ni.f = total_cost
          heapq.heappush(P, (total_cost, ni))
          print("yup not here", ni,gtemp_ni)
        else :
          if gtemp_ni >= pop_node.g:
             continue
        ni.parent = pop_node
        ni.g = gtemp_ni
        total_cost = gtemp_ni + heuristic(states,g_node)
        ni.f = total_cost
        print("states",states)

plot_3d_trajectory(visited_positions, edges, Visited, [0, 0, 0], g_node.state[:3])

