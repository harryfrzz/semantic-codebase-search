package main

// TODO - Need to add more colours
// TODO - Need to make the title look better
// TODO - Improved layout

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/glamour"
	"github.com/charmbracelet/lipgloss"
)

type state int

const (
	inputView state = iota
	resultView
	errorView
)

type model struct {
	textInput textinput.Model
	viewport  viewport.Model
	spinner   spinner.Model
	state     state
	result    string
	err       error
	loading   bool
	renderer  *glamour.TermRenderer
}

type searchResultMsg struct {
	result string
	err    error
}

func initialModel() model {
	ti := textinput.New()
	ti.Placeholder = "Enter your codebase query (e.g., 'where is the code for new tab')"
	ti.Focus()
	ti.CharLimit = 200
	ti.Width = 100

	vp := viewport.New(80, 20)
	vp.SetContent("")

	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("205"))

	renderer, err := glamour.NewTermRenderer(
		glamour.WithAutoStyle(),
		glamour.WithWordWrap(78),
	)
	if err != nil {
		log.Fatal(err)
	}

	return model{
		textInput: ti,
		viewport:  vp,
		spinner:   s,
		state:     inputView,
		err:       nil,
		loading:   false,
		renderer:  renderer,
	}
}

func (m model) Init() tea.Cmd {
	return textinput.Blink
}

func searchCodebase(query string) tea.Cmd {
	return func() tea.Msg {
		// Add a small delay to show the spinner
		time.Sleep(500 * time.Millisecond)

		// Get current working directory
		wd, _ := os.Getwd()

		// Try multiple Python commands
		pythonCommands := []string{"python", "python3", "py"}

		var lastOutput []byte
		var lastErr error

		for _, pythonCmd := range pythonCommands {
			// Check if Python command exists
			_, err := exec.LookPath(pythonCmd)
			if err != nil {
				continue // Try next Python command
			}

			entryPointPath := filepath.Join(wd, "core_main", "entry_point.py")

			// Check if the file exists
			if _, err := os.Stat(entryPointPath); os.IsNotExist(err) {
				lastErr = fmt.Errorf("entry_point.py not found at: %s", entryPointPath)
				continue
			}

			// Execute the Python script
			cmd := exec.Command(pythonCmd, entryPointPath, query)
			cmd.Dir = wd

			// Set environment variables
			env := os.Environ()
			env = append(env, "PYTHONIOENCODING=utf-8")
			cmd.Env = env

			output, err := cmd.CombinedOutput()
			lastOutput = output
			lastErr = err

			if err == nil {
				return searchResultMsg{
					result: string(output),
					err:    nil,
				}
			}

			break
		}

		// Return detailed error information
		errorMsg := fmt.Sprintf("PYTHON SCRIPT ERROR\n")
		errorMsg += strings.Repeat("=", 50) + "\n\n"
		errorMsg += fmt.Sprintf("Command: %s\n", "python core_main/entry_point.py")
		errorMsg += fmt.Sprintf("Working Directory: %s\n", wd)
		errorMsg += fmt.Sprintf("Query: %s\n\n", query)

		if lastErr != nil {
			errorMsg += fmt.Sprintf("Exit Code: %s\n\n", lastErr.Error())
		}

		errorMsg += "PYTHON OUTPUT:\n"
		errorMsg += strings.Repeat("-", 30) + "\n"

		if len(lastOutput) > 0 {
			errorMsg += string(lastOutput)
		} else {
			errorMsg += "(No output received from Python script)"
		}

		return searchResultMsg{
			result: "",
			err:    fmt.Errorf(errorMsg),
		}
	}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch m.state {
		case inputView:
			switch msg.Type {
			case tea.KeyEnter:
				if len(strings.TrimSpace(m.textInput.Value())) > 0 {
					m.loading = true
					m.err = nil // Clear previous errors
					return m, tea.Batch(
						m.spinner.Tick,
						searchCodebase(m.textInput.Value()),
					)
				}
			case tea.KeyCtrlC, tea.KeyEsc:
				return m, tea.Quit
			}
		case resultView, errorView:
			switch msg.Type {
			case tea.KeyCtrlC, tea.KeyEsc:
				return m, tea.Quit
			case tea.KeyEnter:
				// Go back to input view
				m.state = inputView
				m.textInput.SetValue("")
				m.textInput.Focus()
				m.result = ""
				m.err = nil
				m.loading = false
				return m, nil
			}
		}

	case searchResultMsg:
		m.loading = false
		if msg.err != nil {
			m.err = msg.err
			m.viewport.SetContent(msg.err.Error())
			m.state = errorView // Switch to error view
		} else {
			// Render markdown content
			rendered, err := m.renderer.Render(msg.result)
			if err != nil {
				// If markdown rendering fails, use plain text
				m.viewport.SetContent(msg.result)
			} else {
				m.viewport.SetContent(rendered)
			}
			m.result = msg.result
			m.state = resultView
		}
		return m, nil

	case tea.WindowSizeMsg:
		m.viewport.Width = msg.Width
		m.viewport.Height = msg.Height - 5

		// Update renderer width
		if m.renderer != nil {
			renderer, err := glamour.NewTermRenderer(
				glamour.WithAutoStyle(),
				glamour.WithWordWrap(msg.Width-4),
			)
			if err == nil {
				m.renderer = renderer
			}
		}
	}

	// Update components based on state
	switch m.state {
	case inputView:
		if m.loading {
			m.spinner, cmd = m.spinner.Update(msg)
		} else {
			m.textInput, cmd = m.textInput.Update(msg)
		}
	case resultView, errorView:
		m.viewport, cmd = m.viewport.Update(msg)
	}

	return m, cmd
}

func (m model) View() string {
	switch m.state {
	case inputView:
		view := "Codebase Search Assistant\n"
		view += strings.Repeat("=", 50) + "\n\n"

		if m.loading {
			view += fmt.Sprintf("%s Searching codebase...\n", m.spinner.View())
		} else {
			view += fmt.Sprintf("%s\n\n", m.textInput.View())
			view += "(Press Enter to search, Esc to quit)"
		}

		return view

	case resultView:
		view := "Search Results (Rendered with Markdown)\n"
		view += strings.Repeat("=", 50) + "\n\n"
		view += m.viewport.View()
		view += "\n\n(Press Enter to search again, Esc to quit)"
		return view

	case errorView:
		view := "Error Details\n"
		view += strings.Repeat("=", 50) + "\n\n"
		view += m.viewport.View()
		view += "\n\n(Press Enter to try again, Esc to quit)"
		return view
	}

	return ""
}

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		log.Fatal(err)
	}
}
