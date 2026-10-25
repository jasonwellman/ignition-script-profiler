# Ignition Perspective Script Execution Profiler & Analysis Suite

A lightweight, zero-config performance monitoring and error-tracking utility designed for Inductive Automation's Ignition platform. 

This suite allows developers to track script execution times, capture unhandled exceptions, and analyze runtime history using native Perspective components—all without polluting your Gateway logs.

---

## Features
* **Universal `@profiler` Decorator**: Easily wrap project library functions, Perspective transforms, or Gateway event scripts.
* **MS SQL Server Backend**: Securely logs execution duration, status, and stack traces.
* **Built-In Perspective UI**: Dynamic XY charts and performance analytics tables to spot latency instantly.
* **Data Maintenance**: Includes utilities to quickly clean up historical database logs.

---

## Prerequisites
* **Ignition 8.x** (Perspective Module enabled)
* **Microsoft SQL Server (2016+)**

---

## Installation
1. Download the latest release from the Ignition Exchange (https://inductiveautomation.com/exchange/3003/overview).
2. Import the resource into your Ignition project.
3. Configure your database connection to point to your MS SQL Server instance.
4. The Gateway startup hook will automatically configure the required schema on startup.

---

## Usage Example
Simply add the decorator to any function you wish to monitor:

```python

@scriptProfiler.profiler()
def my_heavy_query_script(equipment_id):
    # Your standard Ignition logic here
    return
