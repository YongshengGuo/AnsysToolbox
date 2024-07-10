
import System.Drawing
import System.Windows.Forms

from System.Drawing import *
from System.Windows.Forms import *

from System.Windows.Forms import Cursors
from functools import wraps
def WaitCursor(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        form = args[0]
        form.Cursor = Cursors.WaitCursor
        func(*args, **kwargs)
        form.Cursor = Cursors.Default
    return wrapped_function


class Form1(Form):
	def __init__(self):
		self.InitializeComponent()
		self.layout = None
	
	def InitializeComponent(self):
		self._groupBox1 = System.Windows.Forms.GroupBox()
		self._label1 = System.Windows.Forms.Label()
		self._textBox_netReg = System.Windows.Forms.TextBox()
		self._button_viewNets = System.Windows.Forms.Button()
		self._label2 = System.Windows.Forms.Label()
		self._textBox_stub = System.Windows.Forms.TextBox()
		self._button_executeBackdrill = System.Windows.Forms.Button()
		self._button_close = System.Windows.Forms.Button()
		self._button_clearBackdrill = System.Windows.Forms.Button()
		self._button_reload = System.Windows.Forms.Button()
		self._tableLayoutPanel1 = System.Windows.Forms.TableLayoutPanel()
		self._tableLayoutPanel2 = System.Windows.Forms.TableLayoutPanel()
		self._tableLayoutPanel3 = System.Windows.Forms.TableLayoutPanel()
		self._groupBox1.SuspendLayout()
		self._tableLayoutPanel1.SuspendLayout()
		self._tableLayoutPanel2.SuspendLayout()
		self._tableLayoutPanel3.SuspendLayout()
		self.SuspendLayout()
		# 
		# groupBox1
		# 
		self._groupBox1.Controls.Add(self._tableLayoutPanel3)
		self._groupBox1.Dock = System.Windows.Forms.DockStyle.Fill
		self._groupBox1.Location = System.Drawing.Point(3, 3)
		self._groupBox1.Name = "groupBox1"
		self._groupBox1.Size = System.Drawing.Size(679, 187)
		self._groupBox1.TabIndex = 0
		self._groupBox1.TabStop = False
		self._groupBox1.Text = "Backdrill On Nets"
		# 
		# label1
		# 
		self._label1.Dock = System.Windows.Forms.DockStyle.Top
		self._label1.Location = System.Drawing.Point(3, 41)
		self._label1.Name = "label1"
		self._label1.Size = System.Drawing.Size(162, 23)
		self._label1.TabIndex = 0
		self._label1.Text = "Net Match(RegRex):"
		self._label1.TextAlign = System.Drawing.ContentAlignment.TopRight
		# 
		# textBox_netReg
		# 
		self._textBox_netReg.Dock = System.Windows.Forms.DockStyle.Top
		self._textBox_netReg.Location = System.Drawing.Point(171, 44)
		self._textBox_netReg.Name = "textBox_netReg"
		self._textBox_netReg.Size = System.Drawing.Size(327, 22)
		self._textBox_netReg.TabIndex = 1
		self._textBox_netReg.Text = ".*"
		# 
		# button_viewNets
		# 
		self._button_viewNets.AutoSize = True
		self._button_viewNets.Location = System.Drawing.Point(504, 44)
		self._button_viewNets.Name = "button_viewNets"
		self._button_viewNets.Size = System.Drawing.Size(107, 27)
		self._button_viewNets.TabIndex = 2
		self._button_viewNets.Text = "View Match Nets"
		self._button_viewNets.UseVisualStyleBackColor = True
		self._button_viewNets.Visible = False
		self._button_viewNets.Click += self.Button_viewNetsClick
		# 
		# label2
		# 
		self._label2.AutoSize = True
		self._label2.Dock = System.Windows.Forms.DockStyle.Top
		self._label2.ImageAlign = System.Drawing.ContentAlignment.MiddleRight
		self._label2.Location = System.Drawing.Point(3, 82)
		self._label2.Name = "label2"
		self._label2.Size = System.Drawing.Size(162, 17)
		self._label2.TabIndex = 3
		self._label2.Text = "Backdrill Stub:"
		self._label2.TextAlign = System.Drawing.ContentAlignment.TopRight
		# 
		# textBox_stub
		# 
		self._textBox_stub.Dock = System.Windows.Forms.DockStyle.Top
		self._textBox_stub.Location = System.Drawing.Point(171, 85)
		self._textBox_stub.Name = "textBox_stub"
		self._textBox_stub.Size = System.Drawing.Size(327, 22)
		self._textBox_stub.TabIndex = 4
		self._textBox_stub.Text = "8mil"
		# 
		# button_executeBackdrill
		# 
		self._button_executeBackdrill.Dock = System.Windows.Forms.DockStyle.Top
		self._button_executeBackdrill.Location = System.Drawing.Point(408, 3)
		self._button_executeBackdrill.Name = "button_executeBackdrill"
		self._button_executeBackdrill.Size = System.Drawing.Size(129, 40)
		self._button_executeBackdrill.TabIndex = 3
		self._button_executeBackdrill.Text = "Execute Backdrill"
		self._button_executeBackdrill.UseVisualStyleBackColor = True
		self._button_executeBackdrill.Click += self.Button_executeBackdrillClick
		# 
		# button_close
		# 
		self._button_close.Dock = System.Windows.Forms.DockStyle.Top
		self._button_close.Location = System.Drawing.Point(543, 3)
		self._button_close.Name = "button_close"
		self._button_close.Size = System.Drawing.Size(133, 40)
		self._button_close.TabIndex = 4
		self._button_close.Text = "Close"
		self._button_close.UseVisualStyleBackColor = True
		self._button_close.Click += self.Button_closeClick
		# 
		# button_clearBackdrill
		# 
		self._button_clearBackdrill.Dock = System.Windows.Forms.DockStyle.Top
		self._button_clearBackdrill.Location = System.Drawing.Point(273, 3)
		self._button_clearBackdrill.Name = "button_clearBackdrill"
		self._button_clearBackdrill.Size = System.Drawing.Size(129, 40)
		self._button_clearBackdrill.TabIndex = 5
		self._button_clearBackdrill.Text = "Clear All Backdrill"
		self._button_clearBackdrill.UseVisualStyleBackColor = True
		self._button_clearBackdrill.Click += self.Button_clearBackdrillClick
		# 
		# button_reload
		# 
		self._button_reload.Dock = System.Windows.Forms.DockStyle.Top
		self._button_reload.Location = System.Drawing.Point(138, 3)
		self._button_reload.Name = "button_reload"
		self._button_reload.Size = System.Drawing.Size(129, 40)
		self._button_reload.TabIndex = 6
		self._button_reload.Text = "Reload"
		self._button_reload.UseVisualStyleBackColor = True
		self._button_reload.Click += self.Button_reloadClick
		# 
		# tableLayoutPanel1
		# 
		self._tableLayoutPanel1.ColumnCount = 1
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.Controls.Add(self._groupBox1, 0, 0)
		self._tableLayoutPanel1.Controls.Add(self._tableLayoutPanel2, 0, 1)
		self._tableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
		self._tableLayoutPanel1.Location = System.Drawing.Point(0, 0)
		self._tableLayoutPanel1.Name = "tableLayoutPanel1"
		self._tableLayoutPanel1.RowCount = 2
		self._tableLayoutPanel1.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 68.9655151))
		self._tableLayoutPanel1.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 31.034483))
		self._tableLayoutPanel1.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20))
		self._tableLayoutPanel1.Size = System.Drawing.Size(685, 281)
		self._tableLayoutPanel1.TabIndex = 7
		# 
		# tableLayoutPanel2
		# 
		self._tableLayoutPanel2.ColumnCount = 5
		self._tableLayoutPanel2.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20))
		self._tableLayoutPanel2.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20))
		self._tableLayoutPanel2.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20))
		self._tableLayoutPanel2.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20))
		self._tableLayoutPanel2.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20))
		self._tableLayoutPanel2.Controls.Add(self._button_reload, 1, 0)
		self._tableLayoutPanel2.Controls.Add(self._button_close, 4, 0)
		self._tableLayoutPanel2.Controls.Add(self._button_executeBackdrill, 3, 0)
		self._tableLayoutPanel2.Controls.Add(self._button_clearBackdrill, 2, 0)
		self._tableLayoutPanel2.Dock = System.Windows.Forms.DockStyle.Fill
		self._tableLayoutPanel2.Location = System.Drawing.Point(3, 196)
		self._tableLayoutPanel2.Name = "tableLayoutPanel2"
		self._tableLayoutPanel2.RowCount = 2
		self._tableLayoutPanel2.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 100))
		self._tableLayoutPanel2.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 36))
		self._tableLayoutPanel2.Size = System.Drawing.Size(679, 82)
		self._tableLayoutPanel2.TabIndex = 1
		# 
		# tableLayoutPanel3
		# 
		self._tableLayoutPanel3.ColumnCount = 4
		self._tableLayoutPanel3.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25))
		self._tableLayoutPanel3.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 49.4799423))
		self._tableLayoutPanel3.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 16.7904911))
		self._tableLayoutPanel3.ColumnStyles.Add(System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 8.46954))
		self._tableLayoutPanel3.Controls.Add(self._label2, 0, 2)
		self._tableLayoutPanel3.Controls.Add(self._textBox_stub, 1, 2)
		self._tableLayoutPanel3.Controls.Add(self._textBox_netReg, 1, 1)
		self._tableLayoutPanel3.Controls.Add(self._label1, 0, 1)
		self._tableLayoutPanel3.Controls.Add(self._button_viewNets, 2, 1)
		self._tableLayoutPanel3.Dock = System.Windows.Forms.DockStyle.Fill
		self._tableLayoutPanel3.Location = System.Drawing.Point(3, 18)
		self._tableLayoutPanel3.Name = "tableLayoutPanel3"
		self._tableLayoutPanel3.RowCount = 4
		self._tableLayoutPanel3.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25))
		self._tableLayoutPanel3.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25))
		self._tableLayoutPanel3.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25))
		self._tableLayoutPanel3.RowStyles.Add(System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 25))
		self._tableLayoutPanel3.Size = System.Drawing.Size(673, 166)
		self._tableLayoutPanel3.TabIndex = 5
		# 
		# Form1
		# 
		self.ClientSize = System.Drawing.Size(685, 281)
		self.Controls.Add(self._tableLayoutPanel1)
		self.Name = "Form1"
		self.Text = "Auto Backdrill"
		self._groupBox1.ResumeLayout(False)
		self._tableLayoutPanel1.ResumeLayout(False)
		self._tableLayoutPanel2.ResumeLayout(False)
		self._tableLayoutPanel3.ResumeLayout(False)
		self._tableLayoutPanel3.PerformLayout()
		self.ResumeLayout(False)

	def Button_viewNetsClick(self, sender, e):
		pass

	def Button_closeClick(self, sender, e):
		self.Close()

	@WaitCursor
	def Button_executeBackdrillClick(self, sender, e):

	    self.layout.initDesign()
	    netNames = self.layout.nets.getRegularNets(self._textBox_netReg.Text)
	    stub = self._textBox_stub.Text
	    for net in netNames:
	        self.layout.nets[net].backdrill(stub=stub)

	@WaitCursor
	def Button_clearBackdrillClick(self, sender, e):
		self.layout.initDesign()
		for via in self.layout.vias:
			via.clearBackdrill()

	@WaitCursor
	def Button_reloadClick(self, sender, e):
		self.layout.initDesign()

	def Button_viewNetsClick(self, sender, e):
		pass