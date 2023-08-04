import { Component, OnInit } from '@angular/core';
import { CreateScriptService } from 'src/app/_service/create-script.service';

@Component({
  selector: 'app-review-scripts',
  templateUrl: './review-scripts.component.html',
  styleUrls: ['./review-scripts.component.sass']
})
export class ReviewScriptsComponent implements OnInit {

  public scripts: any = [];

  constructor(
    private createScriptService: CreateScriptService
  ) { }

  ngOnInit() {
    this.createScriptService.getReviewScripts().subscribe(
      (res) => this.scripts = res['data'],
      console.error
    )
  }
}
