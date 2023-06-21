import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
// import * as ClassicEditor from '@ckeditor/ckeditor5-build-classic';
//import { EditorChangeContent, EditorChangeSelection } from 'ngx-quill'

@Component({
  selector: 'app-script-slide',
  templateUrl: './script-slide.component.html',
  styleUrls: ['./script-slide.component.sass']
})
export class ScriptSlideComponent implements OnInit {
  @Input() slide: any;
  public oldSlide: any = [];
  @Input() index: number;
  @Output() removeSlideEmitter = new EventEmitter<number>();
  @Output() saveSlideEmitter = new EventEmitter<any>();
  @Output() insertSlideEmitter = new EventEmitter<number>();
  @Output() duplicateSlideEmitter = new EventEmitter<number>();
  @Output() moveSlideEmitter = new EventEmitter<any>();
  @Input() view: boolean = false;
  @Input() nav:any;
  @Input() autosave: boolean = false;
  @Input() titleVisualCue: string;
  public comment = false;
  public ckEditorCue: boolean = false;
  public ckEditorNarration: boolean = false;
  public visual_cue : number = 0;
  public visual_cue_char : number = 0;
  narration = 0;
  public narration_char : number = 0;

  public quillStyles = {
    'height': '200px',
    'border': '1px solid #ccc',
    'margin': 'auto',
    'max-width': '600px'
  }

  editorForm: FormGroup;

  

  onChange(event: any): void {
  if(event == ''){
    this.visual_cue = 0;
    this.visual_cue_char = 0;
  }else
  if(event == null){
    this.visual_cue = 0;
    this.visual_cue_char = 0;
  }else{
  var s = event;
  var regex  = /(<([^>]+)>)/ig;
  var sn = s.replace(regex, " ");
  var s_char = s.replace(regex, "");
  this.visual_cue_char = s_char.length;
  var regex_space = /\s{2,}/ig;
  var regex_space_c = /\s{1,}/ig;
  var s1 = sn.trim().replace(regex_space,' ')
  var s2 = sn.trim().replace(regex_space_c,'')
  var len = s1.split(" ").length;
  var char_len = s2.length;
  this.visual_cue = len;
  }
}

  onNarrationChange(event: any): void {
  if(event == ''){
    this.narration = 0;
    this.narration_char = 0;
  }else
  if(event == null){
    this.narration = 0;
    this.narration_char = 0;
  }else{
  var s = event;
  var regex  = /(<([^>]+)>)/ig;
  var sn = s.replace(regex, " ");
  var s_char = s.replace(regex, "");
  this.narration_char = s_char.length;
  var regex_space = /\s{2,}/ig;
  var regex_space_c = /\s{1,}/ig;
  var s1 = sn.trim().replace(regex_space,' ')
  var len = s1.split(" ").length;
  this.narration = len;
  }
  }

  

  // public Editor = ClassicEditor;
  // public ckeditorConfig = {
  //   toolbar: ['heading', '|', 'bold', 'italic', 'bulletedList', 'numberedList', '|', 'undo', 'redo']
  // }

  modules = {}
  constructor() {
    this.modules = {
      toolbar: [
        ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
        // ['blockquote', 'code-block'],

        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        [{ 'script': 'sub' }, { 'script': 'super' }],      // superscript/subscript
        // [{ 'indent': '-1' }, { 'indent': '+1' }],          // outdent/indent

        // [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],

        // [{ 'font': [] }],

        ['link', 'image'],

        ['clean'],                                         // remove formatting button
      ]
    }
  }

  public moveSlide(move) {
    this.moveSlideEmitter.emit(
      {
        'index': this.index,
        'move': move
      }
    );
  }
  // argument:void
  // what it does:tells script component the index of the array so that script component can delete that element from the array.
  // returns: void
  public removeSlide() {
    this.removeSlideEmitter.emit(this.index);
  }
  
  public insertSlide() {
    this.insertSlideEmitter.emit(this.index + 1);

  }
  
  public checkSlide() {
    this.oldSlide.cue = this.slide.cue;
    this.oldSlide.narration = this.slide.narration;
  }

  public duplicateSlide() {
    this.duplicateSlideEmitter.emit(this.index + 1);
  }

  public saveSlide(isAutosave) {
    if (isAutosave) {
      if (!this.autosave) return;
    }

    if (this.oldSlide.cue != this.slide.cue) {
      this.slide.cue = this.editorForm.get('cue').value
      this.saveSlideEmitter.emit(this.slide);
    }
    else if (this.oldSlide.narration != this.slide.narration) {
      this.slide.narration = this.editorForm.get('narration').value
      this.saveSlideEmitter.emit(this.slide);
    }
    this.ckEditorCue = false;
    this.ckEditorNarration = false;
    this.checkSlide();
  }

  public changeNarrationToEditor() {
    this.ckEditorNarration = true;
  }
  
  
  ngOnInit() {
    this.editorForm = new FormGroup({
      'cue': new FormControl(),
      'narration': new FormControl()
    })
    this.checkSlide()

  }

}

