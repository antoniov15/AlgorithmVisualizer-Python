import pygame
import random
import traceback

# Constants
WIDTH, HEIGHT = 800, 600
BAR_WIDTH = 10
NUM_BARS = WIDTH // BAR_WIDTH
COLORS = {
    'background': (255, 255, 255),
    'default': (0, 0, 0),
    'compare': (255, 0, 0),
    'swap': (0, 255, 0),
    'sorted': (0, 0, 255)  # New color for sorted elements
}

def generate_random_array():
    return random.sample(range(1, HEIGHT), NUM_BARS)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            # Yield current indices being compared and if a swap occurs
            yield arr.copy(), j, j+1, False
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
                yield arr.copy(), j, j+1, True
        if not swapped:
            break
    yield arr.copy(), -1, -1, False  # Sorting completed

def merge_sort(arr):
    """
    Merge sort implementation with visualization steps.
    This is a completely rewritten implementation to fix generator issues.
    """
    # Create a working copy of the array
    array = arr.copy()
    
    # Create auxiliary array for merging
    aux = array.copy()
    
    def merge(low, mid, high):
        """
        Merge two sorted subarrays: array[low..mid] and array[mid+1..high]
        """
        # Copy array elements to auxiliary array
        for k in range(low, high + 1):
            aux[k] = array[k]
            # Visualize copying to auxiliary array
            yield array.copy(), low, mid, high, True
        
        # Pointers for the two subarrays and the destination
        i, j, k = low, mid + 1, low
        
        # Merge back from auxiliary array to original array
        while i <= mid and j <= high:
            # Compare elements
            yield array.copy(), i, j, k, True
            
            if aux[i] <= aux[j]:
                array[k] = aux[i]
                i += 1
            else:
                array[k] = aux[j]
                j += 1
                
            k += 1
            # Visualize after placement
            yield array.copy(), low, mid, high, True
            
        # Copy remaining elements from left subarray
        while i <= mid:
            array[k] = aux[i]
            i += 1
            k += 1
            yield array.copy(), low, mid, high, True
            
        # Copy remaining elements from right subarray
        while j <= high:
            array[k] = aux[j]
            j += 1
            k += 1
            yield array.copy(), low, mid, high, True

    def sort(low, high):
        """
        Recursive merge sort implementation
        """
        if low < high:
            # Calculate middle point
            mid = (low + high) // 2
            
            # Visualize the current division
            yield array.copy(), low, mid, high, False
            
            # Sort first half
            yield from sort(low, mid)
            
            # Sort second half
            yield from sort(mid + 1, high)
            
            # Merge the sorted halves
            yield from merge(low, mid, high)
    
    # Initial visualization state
    yield array.copy(), -2, -2, -2, False
    
    # Start the sorting process
    try:
        yield from sort(0, len(array) - 1)
    except Exception as e:
        print(f"Error in merge sort algorithm: {e}")
        traceback.print_exc()
    
    # Final visualization state (sorting completed)
    yield array.copy(), -1, -1, -1, False

def draw_array(surface, arr, *args):
    """Enhanced draw function that handles both sorting algorithms"""
    surface.fill(COLORS['background'])
    
    # Default coloring - just draw all bars in default color
    if len(args) == 0:
        for i, val in enumerate(arr):
            pygame.draw.rect(surface, COLORS['default'], (i * BAR_WIDTH, HEIGHT - val, BAR_WIDTH - 1, val))
    
    # Bubble sort visualization (left, right, is_swap)
    elif len(args) == 3:
        left, right, is_swap = args
        for i, val in enumerate(arr):
            color = COLORS['swap'] if is_swap and (i == left or i == right) else \
                   COLORS['compare'] if (i == left or i == right) else \
                   COLORS['default']
            pygame.draw.rect(surface, color, (i * BAR_WIDTH, HEIGHT - val, BAR_WIDTH - 1, val))
    
    # Merge sort visualization with 4 parameters
    elif len(args) == 4:
        start, mid, end, is_merge = args
        
        for i, val in enumerate(arr):
            # Determine color based on merge sort state
            if start == -2 or mid == -2 or end == -2:  # Initial state
                color = COLORS['default']
            elif start == -1 and mid == -1 and end == -1:  # Complete state
                color = COLORS['sorted']
            elif is_merge and start <= i <= end:
                if i <= mid:
                    color = COLORS['compare']  # Left subarray
                else:
                    color = COLORS['swap']     # Right subarray
            elif start <= i <= end:
                color = COLORS['compare']      # Current subarray being processed
            else:
                color = COLORS['default']      # Unprocessed
                
            pygame.draw.rect(surface, color, (i * BAR_WIDTH, HEIGHT - val, BAR_WIDTH - 1, val))
    
    # Fallback for unexpected args
    else:
        for i, val in enumerate(arr):
            pygame.draw.rect(surface, COLORS['default'], (i * BAR_WIDTH, HEIGHT - val, BAR_WIDTH - 1, val))
    
    # pygame.display.update() removed from here
    
def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Algorithm Visualizer")
    clock = pygame.time.Clock()
    
    arr = generate_random_array()
    current_algorithm = "bubble"  # Default algorithm
    generator = bubble_sort(arr)
    
    sorting = True
    speed = 100  # Milliseconds per step
    last_step_time = 0
    running = True
    
    # Font for text rendering
    font = pygame.font.SysFont('Arial', 20)
    
    # Create a text background to prevent clipping
    text_bg_height = 130  # Adjust based on your text needs
    
    while running:
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sorting = not sorting
                elif event.key == pygame.K_r:
                    arr = generate_random_array()
                    if current_algorithm == "bubble":
                        generator = bubble_sort(arr)
                    else:
                        generator = merge_sort(arr)
                    sorting = True
                elif event.key == pygame.K_UP:
                    speed = max(10, speed - 10)
                elif event.key == pygame.K_DOWN:
                    speed += 10
                elif event.key == pygame.K_b:
                    current_algorithm = "bubble"
                    arr = generate_random_array()
                    generator = bubble_sort(arr)
                    sorting = True
                elif event.key == pygame.K_m:
                    current_algorithm = "merge"
                    arr = generate_random_array()
                    generator = merge_sort(arr)
                    sorting = True
        
        # Algorithm step handling
        if sorting and current_time - last_step_time > speed:
            try:
                if current_algorithm == "bubble":
                    current_array, left, right, is_swap = next(generator)
                    draw_array(win, current_array, left, right, is_swap)
                else:  # Merge sort
                    try:
                        next_state = next(generator)
                        
                        # Simplified handling - just pass exactly what we got from the generator
                        if len(next_state) == 5:  # Standard merge sort state
                            draw_array(win, next_state[0], *next_state[1:])
                        else:
                            # Fallback for unexpected state format
                            draw_array(win, next_state[0])
                            
                    except StopIteration:
                        # This is normal - the algorithm has finished
                        sorting = False
                        
                        # Draw the final array with all bars colored as sorted
                        draw_array(win, arr, -1, -1, -1, False)
                        
                        print("Merge sort completed!")
                        continue  # Skip to the next iteration
                    except Exception as e:
                        print(f"Error processing merge sort state: {e}")
                        traceback.print_exc()
                        # Just draw the array without highlighting
                        draw_array(win, arr)
                
                last_step_time = current_time
            except StopIteration:
                sorting = False
                # Mark the algorithm as complete - no need to print "Error"
                print("Algorithm completed!")
        
        # Draw a semi-transparent background for text
        text_bg = pygame.Surface((WIDTH, text_bg_height))
        text_bg.set_alpha(200)  # Adjust transparency (0-255)
        text_bg.fill((240, 240, 240))  # Light gray background
        win.blit(text_bg, (0, 0))
        
        # Draw UI text
        if not sorting:
            text = font.render("Press SPACE to continue", True, (0, 0, 0))
            win.blit(text, (10, 10))
        
        # Show current algorithm and controls
        algo_text = font.render(f"Algorithm: {'Bubble Sort' if current_algorithm == 'bubble' else 'Merge Sort'}", True, (0, 0, 0))
        win.blit(algo_text, (10, 40))
        
        controls_text = font.render("B: Bubble Sort | M: Merge Sort | R: Reset | Space: Pause/Play", True, (0, 0, 0))
        win.blit(controls_text, (10, 70))
        
        speed_text = font.render(f"Speed: {1000/speed:.1f} steps/sec (↑/↓ to change)", True, (0, 0, 0))
        win.blit(speed_text, (10, 100))
        
        # Single display update at the end of the frame
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()