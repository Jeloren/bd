/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
import { formView } from "@web/views/form/form_view";
import { Game, GameBoard } from "@study/js/game";
import { onMounted, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class StudyFormRenderer extends FormRenderer {
  setup() {
    super.setup();
    onMounted(() => {
      const game = new Game(4);
      const board = new GameBoard(game);
    });
  }
}

StudyFormRenderer.template = xml`
    <t t-call="{{ templates.FormRenderer }}" t-call-context="{ __comp__: Object.assign(Object.create(this), { this: this }) }" />
        <div class="container">
            <h1>Найди пару</h1>
            <div class="stats">
                <div>Ходы: 
                    <span id="moves">0</span>
                </div>
                <div>
                    Найдено пар: <span id="pairs">0</span>/
                    <span id="total-pairs">8</span>
                </div>
            </div>
            <div id="game-board"></div>
            <button id="restart-btn">Новая игра</button>

            <div class="win-message" id="win-message">Поздравляем! Вы выиграли!</div>
        </div>`;

export const StudyFormView = {
  ...formView,
  Renderer: StudyFormRenderer,
};
registry.category("views").add("study_form", StudyFormView);
